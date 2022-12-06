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
    status = int(row['Status'])
    db_id = run_query(connection, f"select link_id from earthquakes where link_id = {df_id}")
    if db_id:
        print('')
        # todo: fix bug. syntax error
        # update_eq_table = """UPDATE earthquakes
        #                     SET date_time = '{}',
        #                     local_time_at_epicenter = '{}', status = '{}',
        #                     magnitude = '{}', depth = '{}',
        #                     epicenter_latitude_longitude = '{}',
        #                     antipode = '{}',
        #                     shaking_intensity = '{}',
        #                     felt = '{}',
        #                     primary_data_source = '{}'
        #                     nearest_volcano = '{}'
        #                     estimated_seismic_energy = '{}'
        #                     WHERE external_eq_id = '{}'""".format(
        #                         row['Date & time'],
        #                         row['Local time at epicenter'],
        #                         row['Status'], row['Magnitude'], row['Depth'],
        #                         row['Epicenter latitude / longitude'], row['Antipode'],row['Shaking intensity'],
        #                         row['Felt'], row['Primary data source'], row['Nearest volcano'],
        #                         row['Estimated seismic energy released'], db_id)


        # run_query(connection, update_eq_table)
    else:
        create_eq = """INSERT INTO earthquakes (link_id ,date_time, local_time_at_epicenter, status, magnitude,
                        depth, epicenter_latitude_longitude, antipode, shaking_intensity,felt,primary_data_source,
                               nearest_volcano,estimated_seismic_energy) VALUES
                               ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(
                                df_id,
                                row['Date & time'],
                                row['Local time at epicenter'], status,
                                row['Magnitude'], row['Depth'],
                                row['Epicenter latitude / longitude'],
                                row['Antipode'],
                                row['Shaking intensity'],
                                row['Felt'],
                                row['Primary data source'],
                                row['Nearest volcano'],
                                row['Estimated seismic energy released'])

        run_query(connection, create_eq)
        db_id = run_query(connection, f"select link_id from earthquakes where link_id = {df_id}")

    if row['Nearby towns and cities']:
        for city in row['Nearby towns and cities']:
            city_name = city[1]
            city_distance = int(city[0])
            city_population = int(city[2])
            city_id = run_query(connection, "select id from cities where city_name = %s", city_name)
            if not city_id:
                create_city = """INSERT INTO cities (city_name, population)
                                            VALUES ('{}','{}')""".format(city_name, city_population)

                run_query(connection, create_city)
                # todo: fix bug. city_id does not change
                city_id = run_query(connection, "select id from cities where city_name = %s", city_name)
            if not run_query(connection,
                              f"select id from eq_cities where eq_id = %s and city_id = %s", (db_id, city_id)):
                create_eq_city = """INSERT INTO eq_cities (eq_id, city_id, distance)
                                            VALUES ('{}','{}','{}')""".format(db_id, city_id, city_distance)

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
