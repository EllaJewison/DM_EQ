"""This is the project of Ella, Emuna and Salomé
on the earthquake website
"https://www.allquakes.com/earthquakes/today.html" """
import re
import requests
from bs4 import BeautifulSoup


def create_soup_from_link(link):
    """ creates soup from link """
    page = requests.get(link)  # asking permission from the website to fetch data, If response is 200 it's ok
    my_soup = BeautifulSoup(page.content, "html.parser")  # creating a bs object that takes page.content as an input
    return my_soup


def get_show_more_url(my_soup) -> str:
    """the function returns the url that include show more"""
    script = my_soup.find('div', {'class': 'table-wrap'}).script.text
    url_regex = re.search(r'var url="(.*)"\+"(.*)";', script)
    return url_regex.group(1) + url_regex.group(2)


def extract_show_more_soup(my_soup):
    """return a beautifulsoup object of all additional rows"""
    url = get_show_more_url(my_soup)
    new_soup = create_soup_from_link(url)
    return new_soup


def get_date(quake_data_cells):
    """return the date of the earthquake"""
    return quake_data_cells[0].contents[0]


def get_magnitude(quake_data_cells):
    """return the magnitude of the earthquake"""
    return quake_data_cells[1].contents[0].text


def get_depth(quake_data_cells):
    """return the depth of the earthquake"""
    return quake_data_cells[1].contents[2].replace('\xa0', '')


def get_nearest_volcano(quake_data_cells):
    """return the nearest volcano of the earthquake"""
    return quake_data_cells[2].text


def get_location(quake_data_cells):
    """return the location of the earthquake"""
    return quake_data_cells[3].text.rstrip('I FELT IT')


def get_details_url(quake_data_cells):
    """return the details url  to show more about the earthquake"""
    return quake_data_cells[4].find("a")["href"]


def extract_data_from_quakes(quakes) -> tuple:
    """ This will take the table and make it readable-ish waiting until we can use pandas :) """

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


def main_scrapper_p1():
    """ This will scrap all the updated data and more details about each earthquake"""
    url = "https://www.allquakes.com/earthquakes/today.html"
    soup = create_soup_from_link(url)
    quakes = get_eq(soup)

    show_more_soup = extract_show_more_soup(soup)
    quakes_show_more = get_eq(show_more_soup)

    table_eq_dirty = quakes + quakes_show_more
    data_dict, details_dict = extract_data_from_quakes(table_eq_dirty)

    # printing all data
    print('\nMain Page Table Information\n')
    for q_id in data_dict:
        print(f'{data_dict[q_id]}')


    for idx, q_id in enumerate(details_dict):
        print(f'\ndetails of earthquake num {idx}, id = {q_id}')
        for raw in details_dict[q_id]:
            print(raw)
        print('\n\n')


def main():
    main_scrapper_p1()


if __name__ == '__main__':
    main()
