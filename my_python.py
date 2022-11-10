"""This is the project of Ella, Emuna and Salomé
on the earthquake website
"https://www.allquakes.com/earthquakes/today.html" """

import requests
from bs4 import BeautifulSoup


def create_soup_from_link(link):
    """ creates soup from link """
    page = requests.get(link)  # asking permission from the website to fetch data, If response is 200 its ok
    my_soup = BeautifulSoup(page.content, "html.parser")  # creating a bs object that takes page.content as an input
    return my_soup


def builds_table_eq(my_soup):
    """ This function will build a table with all the earthquakes visible from the 1st page.
     It will return something unreadable by humankind """
    table_eq = my_soup.find('table', id="qTable")
    return table_eq  # at this stage it is not readable for a human


def get_show_more_url(my_soup) -> str:
    """the function returns the url that include show more"""
    script = str(my_soup.find('div', {'class': 'table-wrap'}).script)
    script = script.replace('"', ' ')
    url = ''.join((script.split())[13:16:2])
    return url


def builds_table_show_more(my_soup):
    url = get_show_more_url(my_soup)
    table = create_soup_from_link(url)
    return table


def cleans_from_html_nonsense(table) -> list:
    """ This will take the table and make it readable-ish waiting until we can use pandas :) """

    cells = []
    for i in table.find_all('td'):
        title = i.text
        cells.append(title)

    headers = cells[0:6]
    table = []
    print("rows of clean table")
    for i in range(7, len(cells), len(headers)):
        row = cells[i:i + 6]
        print(row)
        table.append(row)

    return table


def get_eq(table):
    """this finds all the earthquakes from magnitude 2 to magnitude 5"""
    return table.find_all(class_=lambda text: text in ['q2', 'q3', 'q4', 'q5'])


# we will need the function later on
# def find_quake_id(table) -> list:
#     """ function that creates a list of quake ID. We will need it for getting the info on the second page
#     Used for function in second page
#     """
#     quakes = get_eq(table)
#     quake_id_list = []
#     for q in quakes:
#         eq_id = q.get('id')
#         quake_id_list.append(eq_id)
#     return quake_id_list


def find_url_in_table_eq(table) -> list:
    """ This will find all the URL links in the table EQ and return a list of URL
    Used in function for second page
    """
    quakes = get_eq(table)
    url_list = []
    for q in quakes:
        info_link = (q.find_all("a"))[-1]
        link_url = info_link["href"]
        url_list.append(link_url)
    # print(url_list)
    return url_list


def scrap_from_p2(quake_url) -> object:
    """ This function takes the quake id and the url link of an earthquake,  and opens the "more page" and
    hopefully retrieves the data  """
    url = "https://www.volcanodiscovery.com/" + quake_url
    my_soup = create_soup_from_link(url)
    table_p2 = []
    table_rows = my_soup.find_all('tr')
    print("print inner page more tables by row")
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        print(row)
        table_p2.append(row)
    return table_p2


def main_scrapper_p1():
    """ This will scrap the data from the table in the 1st page """
    url = "https://www.allquakes.com/earthquakes/today.html"
    soup = create_soup_from_link(url)
    # table_eq_dirty = builds_table_eq()
    table_eq_dirty = builds_table_show_more(soup)
    table_eq = cleans_from_html_nonsense(table_eq_dirty)
    # print('the main table data:\n', table_eq)

    url_list = find_url_in_table_eq(table_eq_dirty)
    # quake_id_list = find_quake_id(table_eq_dirty)#we will

    # this scrapes the second page !!!!!!!!!!
    counter = 1
    # tuple_id = zip(quake_id_list, url_list)
    for elem in url_list:
        # print(elem)
        table_p2 = scrap_from_p2(elem)
        print('Table num: ', counter)
        counter += 1
        # print('table_p2 : ', table_p2)


def main():
    main_scrapper_p1()


if __name__ == '__main__':
    main()
