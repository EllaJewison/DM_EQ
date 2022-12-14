"""This is the project of Ella, Emuna and Salomé
on the earthquake website
"https://www.allquakes.com/earthquakes/today.html" """
import argparse
import re
import sys
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from cleaning_converting import convert
from datetime import datetime, date, timedelta
import uptade_database
import API_scraper_v1
import logging

MAIN_URL = 'https://www.volcanodiscovery.com/'
LINK = 'https://www.allquakes.com/earthquakes/archive/'

HELP_MESSAGE = """This is a CLI to scrape specific information about earthquakes.
the program will scrape all the relevant information (by date, magnitude) and will update the information
in the database.

Usage:
scraper.py [-h] [--date DATE]
            [--magnitude MAGNITUDE]
            [--n_rows NUMBER]

options:
  -h, --help            show this help message and exit
  --date START_DATE END_DATE(optional) 
  --magnitude FROM_MAGNITUDE TO_MAGNITUDE(optional)
  --n_rows NUMBER

Examples:
1. scraper.py --date 12/11/2022 14/11/2022 -> will scrape all earthquakes from 12/11/2022 to 14/11/2022
2. scraper.py --date 12/11/2022 --magnitude 3.6 8.1 ->
    will scrape all earthquakes from 12/11/2022 until today that have magnitude between 3.6 to 8.1
3. scraper.py --date 12/11/2022 --magnitude 3.6  ->
    will srcape all earthquakes from 12/11/2022 until today
    that have magnitude above 3.6
4. scraper.py --magnitude 7 --n_rows 100 -> will scrape all earthquakes that have magnitude above 7
    limited to 100 first earthquakes
"""

logging.basicConfig(filename='scraper.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class DateAction(argparse.Action):
    """ This class is used to select the dates of wanted earthquakes to scrape. It is used from the command line or in
    configuration in the IDE"""
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            setattr(namespace, self.dest, None)
            return

        if len(values) > 2:
            raise ValueError(f'expected start and end date values. got {len(values)} args: {values}\n')
        # expected at most 2 values, got {len(values)}
        try:
            start_date = datetime.strptime(values[0], '%d/%m/%Y')
        except ValueError as e:
            raise ValueError(f'Could not convert {values[0]} to date.\n {e}')

        end_date = start_date

        if len(values) == 2:
            try:
                end_date = datetime.strptime(values[1], '%d/%m/%Y')
            except ValueError as e:
                raise ValueError(f'Could not convert {values[1]} to date.\n {e}')

        if end_date < start_date:
            raise ValueError(f'Start date {start_date} must be before end date {end_date}\n')
        setattr(namespace, self.dest, (start_date, end_date))


class MagnitudeAction(argparse.Action):
    """ This class is used to select the wanted magnitude of earthquakes to scrop. It is used the command line or in
    configuration from the IDE"""
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            setattr(namespace, self.dest, None)
            return
        if len(values) > 2:
            raise ValueError(f'expected at most 2 values for magnitude range. got {len(values)} args: {values}\n')
        try:
            from_magnitude = float(values[0])
            to_magnitude = float(values[1]) if len(values) == 2 else None
        except ValueError:
            raise ValueError(f'magnitude expected to be decimal number, got {values}')
        if to_magnitude and from_magnitude > to_magnitude:
            raise ValueError(f'{from_magnitude} must be less than {to_magnitude}')
        if from_magnitude < 0 or (to_magnitude and to_magnitude < 0):
            raise ValueError(f'magnitude must be positive, got {from_magnitude}, {to_magnitude}')
        setattr(namespace, self.dest, (from_magnitude, to_magnitude))


def create_soup_from_link(link):
    """ Finds all the html information from the url link passed in the input. Returns a beautifull soup object
     containing the page content. """
    page = requests.get(link)  # asking permission from the website to fetch data, If response is 200 it's ok
    my_soup = BeautifulSoup(page.content, "html.parser")  # creating a bs object that takes page.content as an input
    return my_soup


def get_show_more_url(my_soup) -> str:
    """ This function receives the html from the website and returns the url to access the "show more"
    button and get the complete list of earthquakes. TO sum up it allows access to the page with all the detailed
    information about each earthquake """
    script = my_soup.find('div', {'class': 'table-wrap'}).script.text
    url_regex = re.search(r'var url="(.*)"\+"(.*)";', script)
    return url_regex.group(1) + url_regex.group(2)


def extract_show_more_soup(my_soup):
    """ Finds all the html information from the url link passed in the input (here it will return
     all additional rows from the show more button). It returns a beautifull soup object"""
    url = get_show_more_url(my_soup)
    new_soup = create_soup_from_link(url)
    return new_soup


def get_magnitude(quake_data_cells):
    """return the magnitude of the earthquake"""
    return quake_data_cells[1].contents[0].text


def get_details_url(quake_data_cells):
    """return the details url to show more about the earthquake"""
    return quake_data_cells[4].find("a")["href"]


def get_all_dates(args):
    """ This function gets the input dates from the client and returns a list of all links matching the date range
     queried by the client."""
    try:
        if not args.date:
            logger.info('scrape earthquakes from the last 48 hours')
            return ["https://www.allquakes.com/earthquakes/today.html"]
        elif len(args.date) == 2:
            today = datetime.now()
            start_date = args.date[0]
            end_date = args.date[1]  # perhaps date.now()
            delta = end_date - start_date  # returns timedelta
            list_of_dates = []
            if today > args.date[0] and today > args.date[1]:  # making sure date the second date is the passed
                for i in range(delta.days + 1):
                    day = start_date + timedelta(days=i)
                    list_of_dates.append(day)
                logger.info(f'scrape earthquakes from dates {list_of_dates}')
                return [LINK + d.strftime("%Y-%b-%d").lower() + '.html' for d in list_of_dates]
        elif len(args.date) == 1:
            logger.info(f'scrape earthquakes from day {args.date[0]}')
            return [LINK + args.date[0].strftime("%Y-%b-%d").lower() + '.html']
    except ValueError:
        logger.error("failed to create date list from user date range")
        raise ValueError(f'The date format is invalid')


def extract_ids_filter_by_mag(quakes, args) -> dict:
    """
    This function reads through the HTML contend of quakes and returns a dictionary with the earthquake id as a key
    and the corresponding url as a value, and also filters by the user requested magnitude. This url is the link to the second page, with the complete detail about the
    earthquakes.
    """

    id_to_url = {}
    for idx, q in enumerate(quakes):
        eq_id = q.get('id')
        cells = q.find_all('td')
        url = get_details_url(cells)
        magnitude = get_magnitude(cells)

        if args.magnitude:
            try:
                magnitude = float(magnitude)
                if magnitude < args.magnitude[0]:
                    continue
                if args.magnitude[1] and magnitude > args.magnitude[1]:
                    continue
            except ValueError:
                pass

        id_to_url[eq_id] = url

    return id_to_url


def get_eq(soup):
    """this finds all the earthquakes by magnitude"""
    return soup.find_all('tr', {'class': re.compile(r'q\d')})


def scrapper_main_pages_by_dates(args):

    """ This function scrapes all main pages in range of dates requested by the client.
    It scrapes all the earthquakes, including the "show more" earthquakes,
    and returns the earthquakes ID and URl for the more detailed page.
    """

    url_by_dates = get_all_dates(args)
    dict_id_url = {}
    for url in url_by_dates:
        soup = create_soup_from_link(url)
        quakes = get_eq(soup)
        show_more_soup = extract_show_more_soup(soup)
        logger.info(f'press "show more" to see all quakes from url {url}')
        quakes_show_more = get_eq(show_more_soup)
        table_eq_dirty = quakes + quakes_show_more

        dict_id_url.update(extract_ids_filter_by_mag(table_eq_dirty, args))

        if args.n_rows and len(dict_id_url) >= args.n_rows:
            ids, urls = list(dict_id_url.keys()), list(dict_id_url.values())
            return ids[:args.n_rows], urls[:args.n_rows]

    return list(dict_id_url.keys()), list(dict_id_url.values())


def scraping_with_pandas_p2(url):
    """ this function is used to scrape the detailed pages of each earthquake.
    It returns a pandas dataframe of the available data from the second page."""
    page = requests.get(url)
    dfs = pd.read_html(page.text)  # this creates dataframe directly from the table in h
    # df[0] this is the table that we need.
    table_detailed = dfs[0].transpose()
    table_detailed.columns = table_detailed.iloc[0]
    table_detailed = table_detailed.drop(table_detailed.index[0])
    return table_detailed


def scraping_with_pandas_all_earthquakes(id_list, url_list):
    """ this returns a pandas dataframe of all the earthquakes detailed (every p2)"""
    table_detailed_all_earthquakes = pd.DataFrame()
    for idx, link in enumerate(tqdm(url_list, total=len(url_list))):
        table_detailed = scraping_with_pandas_p2(link)
        logger.info(f'scraped all information for quake num {idx}')
        table_detailed_all_earthquakes = pd.concat([table_detailed_all_earthquakes, table_detailed])
    table_detailed_all_earthquakes["eq_id"] = id_list
    logger.info('successfully create dataframe with all earthquakes')
    return table_detailed_all_earthquakes


def main():
    """ This is the main function of the program : it scrapes the earthquakes website. It scraps the individual
     earthquake information and print to the stdout the data as list.
     This main function uses the mainscrapper_p1 and the pandas scaper for page 2
     """

    parser = argparse.ArgumentParser(add_help=HELP_MESSAGE)
    parser.add_argument('--date', nargs='+', action=DateAction)
    parser.add_argument('--magnitude', nargs='+', action=MagnitudeAction)
    parser.add_argument('--n_rows', type=int, action='store')

    try:
        args = parser.parse_args()
        logger.info(f'Parse user args successfully. args are: date = {args.date},'
                    f'magnitude = {args.magnitude}, num of rows = {args.n_rows}')
    except Exception as e:
        print(f'Wrong arguments passed:\n{e}\nUsage instructions:\n {HELP_MESSAGE}')
        logger.error(f'Wrong arguments passed:\n{e}')
        sys.exit()

    ids, urls = scrapper_main_pages_by_dates(args)
    logger.info('Select all quakes for scraping by arguments done.')
    url_list = [MAIN_URL + link for link in urls]
    data = convert(scraping_with_pandas_all_earthquakes(ids, url_list))
    logger.info('convert pandas dataframe columns to sql dtype')
    data = data.astype(object).where(pd.notnull(data), None)

    connection = uptade_database.get_connection(args.mysql_user, args.mysql_password, 'earthquake')
    logger.info('connect to database')
    for _, row in data.iterrows():
        uptade_database.update_database(row, connection)
    logger.info('database updated with all new earthquakes')

    ### scrapping with the API, second par of the scrapping progam.
    # This part of the code calls another file name : API_scraper_v1, please see inside for further information

    dict_of_df = API_scraper_v1.main()
    logger.info('API scrapping done')
    print('API scrapping done')

    uptade_database.update_fire(dict_of_df['Fire'], connection)
    logger.info('database updated with fire data')
    iceberg = dict_of_df['Fire'].astype(object).where(pd.notnull(dict_of_df['Fire']), None)
    uptade_database.update_iceberg(iceberg, connection)
    logger.info('database updated with iceberg data')
    uptade_database.update_volcano(dict_of_df['Volcano'], connection)
    logger.info('database updated with volcano data')

    connection.close()
    logger.info('database updated successfully, connection closed')


if __name__ == '__main__':
    main()
