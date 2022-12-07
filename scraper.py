"""This is the project of Ella, Emuna and Salomé
on the earthquake website
"https://www.allquakes.com/earthquakes/today.html" """
import argparse
import re
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from uptade_database import update_database, get_connection

from datetime import datetime
from cleaning_converting import convert

HELP_MESSAGE = """This is a CLI to scrape specific information about earthquakes.
the program will scrape all the relevant information (by date, magnitude) and will update the information
in the database.

Usage:
scraper.py [-h] [--date DATE]
            [--magnitude MAGNITUDE]
            [--n_rows NUMBER]
            mysql_user mysql_password

positional arguments:
  mysql_user
  mysql_password

options:
  -h, --help            show this help message and exit
  --date START_DATE END_DATE(optional) 
  --magnitude FROM_MAGNITUDE TO_MAGNITUDE(optional)
  --n_rows NUMBER

Examples:
1. scraper.py user password --date 12/11/2022 14/11/2022 -> will scrape all earthquakes from 12/11/2022 to 14/11/2022
2. scraper.py user password --date 12/11/2022 --magnitude 3.6 8.1 ->
    will scrape all earthquakes from 12/11/2022 until today that have magnitude between 3.6 to 8.1
3. scraper.py user password --date 12/11/2022 --magnitude 3.6  ->
    will srcape all earthquakes from 12/11/2022 until today
    that have magnitude above 3.6
4. scraper.py user password --magnitude 7 --n_rows 100 -> will scrape all earthquakes that have magnitude above 7
    limited to 100 first earthquakes
"""


class DateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not values:
            setattr(namespace, self.dest, None)
            return

        if len(values) > 2:
            raise ValueError(f'expected start and end date values. got {len(values)} args: {values}\n')
        # expected at most 2 values, got {len(values)}
        end_date = datetime.now()
        try:
            start_date = datetime.strptime(values[0], '%d/%m/%Y')
        except ValueError as e:
            raise ValueError(f'Could not convert {values[0]} to date.\n {e}')

        if len(values) == 2:
            try:
                end_date = datetime.strptime(values[1], '%d/%m/%Y')
            except ValueError as e:
                raise ValueError(f'Could not convert {values[1]} to date.\n {e}')

        if end_date < start_date:
            raise ValueError(f'Start date {start_date} must be before end date {end_date}\n')
        setattr(namespace, self.dest, (start_date, end_date))


class MagnitudeAction(argparse.Action):
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


def create_soup_from_link(link):
    """ Finds all the html information from the url link passed in the input  """
    page = requests.get(link)  # asking permission from the website to fetch data, If response is 200 it's ok
    my_soup = BeautifulSoup(page.content, "html.parser")  # creating a bs object that takes page.content as an input
    return my_soup


def get_show_more_url(my_soup) -> str:
    """the function receives the html from the website and returns the url to access the "show more"
    button and get the complete list of earthquakes"""
    script = my_soup.find('div', {'class': 'table-wrap'}).script.text
    url_regex = re.search(r'var url="(.*)"\+"(.*)";', script)
    return url_regex.group(1) + url_regex.group(2)


def extract_show_more_soup(my_soup):
    """ Finds all the html information from the url link passed in the input (here it will return
     all additional rows from the show more button)"""
    url = get_show_more_url(my_soup)
    new_soup = create_soup_from_link(url)
    return new_soup


def get_date(quake_data_cells):
    """ Return the date of the earthquake """
    return quake_data_cells[0].contents[0]


def get_magnitude(quake_data_cells):
    """return the magnitude of the earthquake"""
    return quake_data_cells[1].contents[0].text


def get_depth(quake_data_cells):
    """return the depth of the earthquake"""
    try:
        return quake_data_cells[1].contents[2].replace('\xa0', '')
    except IndexError:
        return ''


def get_nearest_volcano(quake_data_cells):
    """return the nearest volcano of the earthquake"""
    return quake_data_cells[2].text


def get_location(quake_data_cells):
    """return the location of the earthquake"""
    return quake_data_cells[3].text.rstrip('I FELT IT')


def get_details_url(quake_data_cells):
    """return the details url to show more about the earthquake"""
    return quake_data_cells[4].find("a")["href"]


def extract_data_from_quakes(quakes, args) -> dict:
    """ this function reformats the scrapped earthquake information into a list  """

    id_to_data_dict = {}
    for idx, q in enumerate(quakes):
        print(f'fetching quake num {idx + 1} data')
        eq_id = q.get('id')
        cells = q.find_all('td')
        url = get_details_url(cells)
        data = [
            get_date(cells),
            get_magnitude(cells),
            get_depth(cells),
            get_nearest_volcano(cells),
            get_location(cells),
            url,
        ]
        if args.magnitude:
            try:
                magnitude = float(data[1])
                if magnitude < args.magnitude[0]:
                    continue
                if args.magnitude[1] and magnitude > args.magnitude[1]:
                    continue
            except ValueError:
                pass
        if args.date:
            try:
                date = datetime.strptime(re.sub(' GMT.*', '', data[0]), '%b %d, %Y %H:%M')
                if date < args.date[0]:
                    continue
                if args.date[1] and date > args.date[1]:
                    continue
            except ValueError:
                pass

        if args.n_rows and len(id_to_data_dict) >= args.n_rows:
            return id_to_data_dict

        id_to_data_dict[eq_id] = data

    return id_to_data_dict


def get_eq(soup):
    """this finds all the earthquakes by magnitude"""
    return soup.find_all('tr', {'class': re.compile(r'q\d')})


def scrap_from_p2(quake_url) -> object:
    """ This function takes the quake id and the url link of an earthquake, opens the "more page" and
    retrieves the data  """
    url = "https://www.volcanodiscovery.com/" + quake_url
    my_soup = create_soup_from_link(url)
    table_p2 = []
    table_rows = my_soup.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        table_p2.append(row)
    return table_p2


def extract_url_list(data_dict):
    """ used to return a list of url for the pandas scapper p2
    """

    url_list = [data_dict[data][5] for data in data_dict.keys() if data is not None]

    return url_list


def main_scrapper_p1(args):
    """ This function takes main page from the url and will scrap all the updated data
    and more details about each earthquake"""
    url = "https://www.allquakes.com/earthquakes/today.html"
    soup = create_soup_from_link(url)
    quakes = get_eq(soup)

    show_more_soup = extract_show_more_soup(soup)
    quakes_show_more = get_eq(show_more_soup)

    table_eq_dirty = quakes + quakes_show_more
    data_dict = extract_data_from_quakes(table_eq_dirty, args)


    url_list = extract_url_list(data_dict)

    return data_dict.keys(), url_list


def scraping_with_pandas_p2(url):
    """ this function is used to scrape the detailed pages of each earthquakes.
    It returns a pandas dataframe of the available data"""
    # testing with one URL
    # url = "https://www.allquakes.com/earthquakes/quake-info/7220305/mag2quake-Nov-26-2022-43km-SE-of-Avalon-CA.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    dfs = pd.read_html(page.text)   # this creates dataframe directly from the table in h
    # tml !! In out case it scraped 2 tables from the page
    # df[0] is  this is the table that we need
    table_detailed = dfs[0].transpose()
    table_detailed.columns = table_detailed.iloc[0]
    table_detailed = table_detailed.drop(table_detailed.index[0])
    return table_detailed


def scraping_with_pandas_all_earthquakes(id_list, url_list):
    """ this returns a pandas dataframe of all the earthquakes detailed (every p2)"""
    table_detailed_all_earthquakes = pd.DataFrame()
    for link in url_list:
        table_detailed = scraping_with_pandas_p2(link)
        table_detailed_all_earthquakes = pd.concat([table_detailed_all_earthquakes, table_detailed])
    table_detailed_all_earthquakes["eq_id"] = id_list
    return table_detailed_all_earthquakes


def main():
    """ function scrapes the earthquakes site. Scrap the individual earthquake
    information and print the data as list.
     This uses the mainscrapper_p1 and the pandas scaper for page 2
     """

    parser = argparse.ArgumentParser(add_help=HELP_MESSAGE)
    parser.add_argument('mysql_user', type=str)
    parser.add_argument('mysql_password', type=str)

    parser.add_argument('--date', nargs='+', action=DateAction)
    parser.add_argument('--magnitude', nargs='+', action=MagnitudeAction)
    parser.add_argument('--n_rows', type=int, action='store')

    try:
        args = parser.parse_args()
    except Exception as e:
        print(f'Wrong arguments passed:\n{e}\nUsage instructions:\n {HELP_MESSAGE}')
        sys.exit()

    id_list, url_list = main_scrapper_p1(args)
    url_main = 'https://www.volcanodiscovery.com/'
    url_list = [url_main + link for link in url_list]
    data = convert(scraping_with_pandas_all_earthquakes(id_list, url_list))
    # data = data.astype(object).where(pd.notnull(data), None)
    data.fillna(0, inplace=True)
    # data.to_csv('/home/emuna/Documents/Itc/DM_EQ/earthquake_clean.csv')
    print(len(data))
    # TO-DO: pass to update db function

    connection = get_connection('earthquake')
    for _, row in data.iterrows():
        update_database(row, connection)


if __name__ == '__main__':
    main()
