import requests
import pandas as pd
import re
from dateutil import parser
import json

API_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"


def get_events_from_api(API_URL):

    """ Calls a get requests form the URL of the API that will provide a json file.
    Then return a dataframe from the events stores in the json file."""

    a = requests.get(API_URL)
    print('Got the json file from the API !')
    dico = a.json()
    df_events = pd.DataFrame.from_dict(data=dico['events'], orient='columns')
    return df_events


def re_organise_df(df):
    """ returns a df with jsut the important columns : title, id and geometr"""
    df_new = df[['title', 'id', 'geometry']]
    return df_new


def get_info_from_geometry(df):
    # s_mag_value = df['geometry'][0].apply(lambda x: x[0]["magnitudeValue"])
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
    types_events2 = ['Drought','Dust and Haze','Earthquake', 'Flood', 'Iceberg','Landslide', 'Manmade', 'Sea',
    'Severe Storms', 'Snow', 'Temperature', 'Volcano', 'Water Color', 'Fire']

    dico = {event: df[df.title.str.contains('.*'+event+'.*', case=False, regex=True)] for event in types_events2}
    return dico

def change_date(df):
    df['date'] = df['date'].apply(lambda x: parser.parse(x))
    return df

# ds = '2012-03-01T10:00:00Z' # or any date sting of differing formats.
# date = parser.parse(ds)



if __name__ == '__main__':
    df = get_events_from_api(API_URL)
    data = re_organise_df(df)
    data2 = get_info_from_geometry(data)
    dict_of_df = find_event(data2)

    # converting time string to datetime object, raise an error but its still working
    dict_of_df['Volcano'] = change_date(dict_of_df['Volcano'])
    dict_of_df['Iceberg'] = change_date(dict_of_df['Iceberg'])
    dict_of_df['Fire'] = change_date(dict_of_df['Fire'])




