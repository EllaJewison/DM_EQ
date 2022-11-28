"""This is the project of Ella, Emuna and Salomé
on the earthquake website
"https://www.allquakes.com/earthquakes/today.html" """
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from tabulate import tabulate



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


def extract_data_from_quakes(quakes) -> tuple:
    """ this function reformats the scrapped earthquake information into a list  """

    id_to_data_dict = {}
    id_to_details = {}
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
        id_to_data_dict[eq_id] = data
        id_to_details[eq_id] = scrap_from_p2(url)

    return id_to_data_dict, id_to_details


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


def extract_url_list(data_dict, details_dict):
    """ used to return a list of url for the pandas scapper p2
    """
    # print('\nMain Page Table Information\n')
    # for q_id in data_dict:
        # print(f'{data_dict[q_id]}')

    # for idx, q_id in enumerate(details_dict):
        # print(f'\ndetails of earthquake num {idx}, id = {q_id}')
        # for raw in details_dict[q_id]:
            # print(raw)
        # print('\n\n')

    url_list = [data_dict[data][5] for data in data_dict.keys() if data is not None]

    return url_list

def main_scrapper_p1():
    """ This function takes main page from the url and will scrap all the updated data
    and more details about each earthquake"""
    url = "https://www.allquakes.com/earthquakes/today.html"
    soup = create_soup_from_link(url)
    quakes = get_eq(soup)

    show_more_soup = extract_show_more_soup(soup)
    quakes_show_more = get_eq(show_more_soup)

    table_eq_dirty = quakes + quakes_show_more
    data_dict, details_dict = extract_data_from_quakes(table_eq_dirty)
    url_list = extract_url_list(data_dict, details_dict)

    return url_list

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


def scraping_with_pandas_all_earthquakes(url_list):
    """ this returns a pandas dataframe of all the earthquakes detailed (every p2)"""
    table_detailed_all_earthquakes = pd.DataFrame()
    for link in url_list:
        table_detailed = scraping_with_pandas_p2(link)
        table_detailed_all_earthquakes = pd.concat([table_detailed_all_earthquakes, table_detailed])
    return table_detailed_all_earthquakes

def main():
    """ function scrapes the earthquakes site. Scrap the individual earthquake
    information and print the data as list.
     This uses the mainscrapper_p1 and the pandas scaper for page 2"""
    url_list = main_scrapper_p1()
    url_main = 'https://www.volcanodiscovery.com/'
    url_list = [url_main+link for link in url_list]
    test = scraping_with_pandas_all_earthquakes(url_list)
    return test

def saves_csv_of_data(df):
    """ saves a CSV of the scrapped data to work with and not wait arounf during scrapping """
    df.to_csv('earthquake.csv', header=True, index=False)

if __name__ == '__main__':
    table_data = main()
    path_Ella = "/Users/ellaistep/Documents/4_ITC/Data_mining_project/DM_EQ"
    table_data.to_csv('earthquake.csv', header=True, index=False)
