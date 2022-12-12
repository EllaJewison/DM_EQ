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
from datetime import datetime,date, timedelta
import uptade_database
import API_scraper_v1


LINK = 'https://www.allquakes.com/earthquakes/archive/'
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


def get_all_dates(args):
    """the function gets the input dates from client and returns a list of all links of dates in range"""
    try:
        if len(args.date)==2:
            today = datetime.now()
            start_date = args.date[0]
            end_date = args.date[1]  # perhaps date.now()
            delta = end_date - start_date  # returns timedelta
            list_of_dates = []
            if today > args.date[0] and today > args.date[1]:  # making sure date the second date is the passed
                for i in range(delta.days + 1):
                    day = start_date + timedelta(days=i)
                    print(day)
                    list_of_dates.append(day)
                return [LINK + d.strftime("%Y-%b-%d").lower() + '.html' for d in list_of_dates]
        elif len(args.date)==1:
            return [LINK +args.date[0].strftime("%Y-%b-%d").lower() + '.html']
        elif len(args.date)==0:
            return ["https://www.allquakes.com/earthquakes/today.html"]
    except ValueError:
        raise ValueError(f'The date format is invalid')





def extract_data_from_quakes(quakes, args) -> dict:
    """
    Exstracts all information
    """

    id_to_url = {}
    for idx, q in enumerate(quakes):
        eq_id = q.get('id')
        cells = q.find_all('td')
        url = get_details_url(cells)
        data = [
            get_date(cells),
            get_magnitude(cells),
            get_depth(cells),
            get_nearest_volcano(cells),
            get_location(cells)
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
                if date < args.date[0]:  # making sure date is in the passed
                    continue
                if args.date[1] and date > args.date[1]:  # making sure date the second date is the passed
                    continue
                    list_dates = get_all_dates(args)  # if dates are okey:
            except ValueError:
                pass

        if args.n_rows and len(id_to_url) >= args.n_rows:
            return id_to_url

        id_to_url[eq_id] = url

    return id_to_url


def get_eq(soup):
    """this finds all the earthquakes by magnitude"""
    return soup.find_all('tr', {'class': re.compile(r'q\d')})


# def get_links_from_client_request(args):
#     """the function will check if clien askeed for specific dates and return deeded links to scrape"""
#     default_url = "https://www.allquakes.com/earthquakes/today.html"
#     if args.date:
#         try:
#             date = datetime.now().strftime('%b %d, %Y %H:%M')
#             if args.date[1] and date > args.date[1]:  # making sure date the second date is the passed
#                 continue
#             if date < args.date[0]:  # making sure date is in the passet
#                 continue
#                 list_dates = get_all_dates(args)  # if dates are okey:
#         except ValueError:
#             pass
#     else:
#         return


def main_scrapper_p1(args):
    """ This function takes main page from the url and will scrap all the updated data
    and more details about each earthquake"""
    #

    url_by_dates = get_all_dates(args)
    dict_id_url = {}
    for url in url_by_dates:
        soup = create_soup_from_link(url)
        quakes = get_eq(soup)
        show_more_soup = extract_show_more_soup(soup)
        quakes_show_more = get_eq(show_more_soup)
        table_eq_dirty = quakes + quakes_show_more

        dict_id_url.update(extract_data_from_quakes(table_eq_dirty, args))

    return dict_id_url


def scraping_with_pandas_p2(url):
    """ this function is used to scrape the detailed pages of each earthquakes.
    It returns a pandas dataframe of the available data"""
    # testing with one URL
    # url = "https://www.allquakes.com/earthquakes/quake-info/7220305/mag2quake-Nov-26-2022-43km-SE-of-Avalon-CA.html"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    dfs = pd.read_html(page.text)  # this creates dataframe directly from the table in h
    # tml !! In out case it scraped 2 tables from the page
    # df[0] is  this is the table that we need
    table_detailed = dfs[0].transpose()
    table_detailed.columns = table_detailed.iloc[0]
    table_detailed = table_detailed.drop(table_detailed.index[0])
    return table_detailed


def scraping_with_pandas_all_earthquakes(id_list, url_list):
    """ this returns a pandas dataframe of all the earthquakes detailed (every p2)"""
    table_detailed_all_earthquakes = pd.DataFrame()
    for link in tqdm(url_list, total=len(url_list)):
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

    dict_id_url = main_scrapper_p1(args)
    url_main = 'https://www.volcanodiscovery.com/'
    url_list = [url_main + link for link in dict_id_url.values()]
    data = convert(scraping_with_pandas_all_earthquakes(dict_id_url.keys(), url_list))
    data = data.astype(object).where(pd.notnull(data), None)

    connection = uptade_database.get_connection(args.mysql_user, args.mysql_password, 'earthquake')
    for _, row in data.iterrows():
        uptade_database.update_database(row, connection)

    ### scrapping with the API.

    dict_of_df = API_scraper_v1.main()
    print('API scrapping done')

    uptade_database.update_fire(dict_of_df['Fire'], connection)
    iceberg = dict_of_df['Fire'].astype(object).where(pd.notnull(dict_of_df['Fire']), None)
    uptade_database.update_iceberg(iceberg, connection)
    uptade_database.update_volcano(dict_of_df['Volcano'], connection)

    connection.close()


if __name__ == '__main__':
    main()
