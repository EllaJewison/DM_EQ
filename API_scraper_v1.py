import requests
import pandas as pd
from dateutil import parser
import logging

logging.basicConfig(filename='scraper.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

API_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"


def get_events_from_api(API_URL):
    """ Calls a get requests form the URL of the API that will provide a json file.
    This function returns a dataframe with the natural events stored in the json file."""

    a = requests.get(API_URL)
    logger.info('Got the json file from the API')
    dico = a.json()
    df_events = pd.DataFrame.from_dict(data=dico['events'], orient='columns')
    return df_events


def re_organise_df(df):
    """ This function returns a dataframe with just the important columns : title, id and geometry """
    df_new = df[['title', 'id', 'geometry']]
    return df_new


def get_info_from_geometry(df):
    """ This function returns a dataframe with the information stored in the given geometry columns.
    It creates 5 new columns to store the main informations of the natural event """
    s_mag_value = df['geometry'].apply(lambda x: x[0]['magnitudeValue'])
    s_mag_unit = df['geometry'].apply(lambda x: x[0]['magnitudeUnit'])
    s_date = df['geometry'].apply(lambda x: x[0]['date'])
    s_type = df['geometry'].apply(lambda x: x[0]['type'])
    s_coord = df['geometry'].apply(lambda x: x[0]['coordinates'])

    # copying df, adding the relevant columns and dropping the geometry one
    df_new = df.join(pd.DataFrame({'magnitude_value': s_mag_value, 'magnitude_unit': s_mag_unit, 'date': s_date, 'coordinates': s_coord, 'type': s_type}))
    df_new.drop(['geometry'], axis=1, inplace=True)
    return df_new


def find_event(df):
    """ Creates a dictionary of dataframe for each event in the dataset"""
    types_events2 = ['Drought', 'Dust and Haze', 'Earthquake', 'Flood', 'Iceberg', 'Landslide', 'Manmade', 'Sea',
    'Severe Storms', 'Snow', 'Temperature', 'Volcano', 'Water Color', 'Fire']

    dico = {event: df[df.title.str.contains('.*'+event+'.*', case=False, regex=True)] for event in types_events2}
    return dico

def change_date(df):
    """ This function changes the date format from string to a proper datatime format"""
    df['date'] = df['date'].apply(lambda x: parser.parse(x))
    return df

def main():
    """ This is the main function that runs the scraper for the API. It gets the event from the API and returns the
    dictionary of natural events """
    df = get_events_from_api(API_URL)
    data = re_organise_df(df)
    data2 = get_info_from_geometry(data)
    logger.info(f'Create event dataframe with all event information')
    dict_of_df = find_event(data2)
    logger.info(f'create dict_of_df with key as event type and value as event dataframe')

    # converting time string to datetime object, raise an error but its still working
    dict_of_df['Volcano'] = change_date(dict_of_df['Volcano'])
    dict_of_df['Iceberg'] = change_date(dict_of_df['Iceberg'])
    dict_of_df['Fire'] = change_date(dict_of_df['Fire'])

    return dict_of_df


if __name__ == '__main__':
    dict_of_df = main()
    print('dict_of_df: ', dict_of_df)





