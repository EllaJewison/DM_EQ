import pymysql
from datetime import datetime
import re
import pandas as pd
import re
import numpy as np


def get_connection(db):
    """everytime we want to connect to db"""
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='password',
                                 database=db,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def extract_cities_info(city_string):
    if city_string is np.nan:
        return np.nan
    city_string = re.sub(r'^.*}}', '', city_string)
    cities = city_string.split('| Show on map | Quakes nearby')
    matches = [re.match(r'(^\d+) .*\) (.*) \(pop: (\d+),(\d+)', city) for city in cities]
    info = [(int(m.group(1)), m.group(2), 1000 * int(m.group(3)) + int(m.group(4))) for m in matches if m]
    return info


def set_nearby_cities(df):

    df['Nearby towns and cities'] = df['Nearby towns and cities'].apply(extract_cities_info)
    return df


def get_connected(db):
    """everytime we want to connect to db"""
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='password',
                                 database=db,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def run_query(connection, query, query_parameters=None):
    with connection.cursor() as cursor:
        result = cursor.execute(query, query_parameters)
        connection.commit()
    return result


def update_database(row, connection):
    cols = ['eq_id', 'Date & time', 'Local time at epicenter', 'Status',
            'Magnitude', 'Depth', 'Epicenter latitude / longitude', 'Antipode',
            'Shaking intensity', 'Felt', 'Primary data source', 'Nearest volcano',
            'Weather at epicenter at time of quake', 'Estimated seismic energy released']

    # eq_id, date_time, status, magnitude, depth,
    # epicenter_lat, epicenter_long, antipode_lat, antipode_long, shaking_intensity, felt,
    # data_source, nearest_volcano, energy_release
    df_id = int(re.findall(r'\d+', row['eq_id'])[0])
    db_id = run_query(connection, f"select eq_id from earthquakes where eq_id = {df_id}")
    if db_id:
        # todo: complete
        update_eq_table = f"""UPDATE earthquakes
                            SET date_time = {row['Date & time']}, status = {row['Status']},
                            magnitude = {row['Magnitude']}, depth = {row['Depth']}, 
                            epicenter_lat = {row['Epicenter latitude / longitude'][0]},
                            epicenter_long = {row['Epicenter latitude / longitude'][1]},
                            antipode_lat = {row['Antipode'][0]}
                            antipode_long = {row['Antipode'][1]},
                            shaking_intensity = {row['Shaking intensity']},
                            felt = {row['Felt']},
                            data_source = {row['Primary data source']}
                            nearest_volcano = {row['Nearest volcano']}
                            energy_release = {row['Estimated seismic energy released']}
                            WHERE external_eq_id = {row['eq_id']}"""
        run_query(connection, update_eq_table)
    else:
        # todo: complete
        create_eq = f"""INSERT INTO earthquakes
                        (eq_id , date_time, status, magnitude, depth,
                        epicenter_lat, epicenter_long ,antipode_lat, antipode_long,
                        shaking_intensity, felt, data_source, nearest_volcano, energy_release) VALUES
                                ({df_id},
                                {row['Date & time']}, {row['Status']},
                                {row['Magnitude']}, {row['Depth']},
                                {row['Epicenter latitude / longitude'][0]},
                                {row['Epicenter latitude / longitude'][1]},
                                {row['Antipode'][0]}
                                {row['Antipode'][1]},
                                {row['Shaking intensity']},
                                {row['Felt']},
                                {row['Primary data source']},
                                {row['Nearest volcano']},
                                {row['Estimated seismic energy released']})"""
        run_query(connection, create_eq)
        db_id = run_query(connection, "select eq_id from earthquakes where external_eq_id = %s", row['id'])

    for city in row['Nearby towns and cities']:
        city_name = city[1]
        city_distance = int(city[0])
        city_population = int(city[2])
        city_id = run_query(connection, "select city_id from cities where city_name = %s", city_name)
        if not city_id:
            create_city = f"""INSERT INTO cities
                                        VALUES (city_name = {city_name},
                                            date_time = {row['Date & time']}
                                            population = {city_population})"""
            run_query(connection, create_city)
            city_id = run_query(connection, "select city_id from cities where city_name = %s", city)
        if not run_query(connection,
                          f"select eq_city_id from eq_cities where eq_id = %s and city_id = %s", (db_id, city_id)):
            create_eq_city = f"""INSERT INTO eq_cities
                                        VALUES (eq_id = {db_id},
                                            city_id = {city_id},
                                            distance = {city_distance})"""  # todo: find distance
            run_query(connection, create_eq_city)


if __name__ == '__main__':
    table_data = pd.read_csv('/home/emuna/Documents/Itc/DM_EQ/earthquake_clean.csv')
    connection = get_connection('earthquake')
    run_query(connection, 'SHOW tables;')
    run_query(connection, 'DESCRIBE eq_cities;')
    run_query(connection, 'DESCRIBE cities;')
    run_query(connection, 'DESCRIBE earthquakes;')
    for _, row in table_data.iterrows():
        update_database(row, connection)
