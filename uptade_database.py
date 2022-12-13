import pymysql
import pandas as pd
import re
import logging

logging.basicConfig(filename='scraper.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_connection(user, password, database=None):
    """This function establishes a connection to the database using the given user and password"""
    connection = pymysql.connect(host='localhost',
                                 user=user,
                                 password=password,
                                 database=database,
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def run_query(connection, query, query_parameters=None):
    """ this is the user function used to execute a query in the sql database
    """
    with connection.cursor() as cursor:
        cursor.execute(query, query_parameters)
        result = cursor.fetchone()
    return result


def run_update(connection, query, query_parameters=None):
    """ this function is called to ???
    """

    with connection.cursor() as cursor:
        result = cursor.execute(query, query_parameters)
        connection.commit()
    return result


def update_database(row, connection):
    """ this function is used to update the database with a new earthquake.
     It checks weather the earthquake ID is already in the database, if not, the databse is updated  """

    df_id = int(re.findall(r'\d+', row['eq_id'])[0])
    status = int(row['Status'])
    db_id = run_query(connection, f"select id from earthquakes where link_id = {df_id}")
    if db_id:
        db_id = db_id['id']
        update_eq_table = """UPDATE earthquakes
                            SET date_time = %s,
                            local_time_at_epicenter = %s, status = %s,
                            magnitude = %s, depth = %s,
                            epicenter_latitude_longitude = '%s',
                            antipode = '%s',
                            shaking_intensity = %s,
                            felt = %s,
                            primary_data_source = %s,
                            nearest_volcano = %s,
                            estimated_seismic_energy = %s
                            WHERE id = %s"""
        values = (row['Date & time'],
                  row['Local time at epicenter'],
                  row['Status'], row['Magnitude'], row['Depth'],
                  row['Epicenter latitude / longitude'],
                  row['Antipode'], row['Shaking intensity'],
                  row['Felt'], row['Primary data source'], row['Nearest volcano'],
                  row['Estimated seismic energy released'], db_id)

        run_query(connection, update_eq_table, values)
        logger.info(f"Updated earthquake {df_id} in earthquakes table")
    else:

        create_eq = """INSERT INTO earthquakes
                        (link_id ,date_time, local_time_at_epicenter, status, magnitude,
                        depth, epicenter_latitude_longitude, antipode, shaking_intensity,felt,primary_data_source,
                               nearest_volcano,estimated_seismic_energy)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, '%s', '%s', %s, %s, %s, %s, %s)"""
        values = (df_id,
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
        run_update(connection, create_eq, values)
        db_id = run_query(connection, f"select id from earthquakes where link_id = {df_id}")
        logger.info(f'Insert earthquake {df_id} into earthquakes table')
        db_id = db_id['id']

    if row['Nearby towns and cities']:
        for city in row['Nearby towns and cities']:
            city_name = city[1]
            city_distance = int(city[0])
            city_population = int(city[2])
            city_id = run_query(connection, "select id from cities where city_name = %s", city_name)
            if not city_id:
                create_city = """INSERT INTO cities (city_name, population)
                                            VALUES (%s, %s)"""

                run_update(connection, create_city, (city_name, city_population))
                city_id = run_query(connection, "select id from cities where city_name = %s", city_name)
                logger.info(f'Insert city {city_name} into cities table')
                city_id = city_id['id']
            else:
                city_id = city_id['id']
            if not run_query(connection,
                             "select id from eq_cities where eq_id = %s and city_id = %s",
                             (db_id, city_id)):
                create_eq_city = """INSERT INTO eq_cities (eq_id, city_id, distance)
                                            VALUES (%s, %s, %s)"""

                run_update(connection, create_eq_city, (db_id, city_id, city_distance))
                logging.info(f"Insert connection between earthquake {df_id} and  city {city_name} to table eq_cities")


def update_fire(df, connection):
    """ This function updates the fire table with the data scraped from the API. Before adding the instance to the table
    it checks if the id is already in the fire table. """

    for _, row in df.iterrows():
        df_id = int(row['id'].lstrip('EONET_'))
        db_id = run_query(connection, f"select id from fire where eonet_id = {df_id}")
        if db_id:
            db_id = db_id['id']
            update_fire = """UPDATE fire SET
                                fire_name = %s,
                                latitude = %s,
                                longitude = %s,
                                date_time = %s
                                WHERE id = %s"""
            values = (row['title'], row['coordinates'][0], row['coordinates'][1], row['date'], db_id)
            run_update(connection, update_fire, values)
            logger.info(f'Update fire {df_id} into fire table')

        else:
            create_fire = """INSERT INTO fire
                        (eonet_id ,fire_name, latitude, longitude, date_time)
                        VALUES
                        (%s, %s, %s, %s, %s)"""
            values = (df_id, row['title'], row['coordinates'][0], row['coordinates'][1], row['date'])
            run_update(connection, create_fire, values)
            logger.info(f'Insert fire {df_id} into fire table')


def update_volcano(df, connection):
    """ This function updates the volcano table with the data scraped from the API. Before adding the instance to the table
    it checks if the id is already in the volcano table. """
    for _, row in df.iterrows():
        df_id = int(row['id'].lstrip('EONET_'))
        db_id = run_query(connection, f"select id from volcano where eonet_id = {df_id}")
        if db_id:
            db_id = db_id['id']
            update_volcano = """UPDATE volcano SET
                                volcano_name = %s,
                                latitude = %s,
                                longitude = %s,
                                date_time = %s
                                WHERE id = %s"""
            values = (row['title'], row['coordinates'][0], row['coordinates'][1], row['date'], db_id)
            run_update(connection, update_volcano, values)
            logger.info(f'Update volcano {df_id} into volcano table')

        else:
            create_volcano = """INSERT INTO volcano
                        (eonet_id ,volcano_name, latitude, longitude, date_time)
                        VALUES
                        (%s, %s, %s, %s, %s)"""
            values = (df_id, row['title'], row['coordinates'][0], row['coordinates'][1], row['date'])
            run_update(connection, create_volcano, values)
            logger.info(f'Insert volcano {df_id} into volcano table')


def update_iceberg(df, connection):
    """     This function updates the iceberg table with the data scraped from the API. Before adding the instance to the table
    it checks if the id is already in the iceberg table. """

    for _, row in df.iterrows():
        df_id = int(row['id'].lstrip('EONET_'))
        db_id = run_query(connection, f"select id from volcano where eonet_id = {df_id}")
        if db_id:
            db_id = db_id['id']
            update_iceberg = """UPDATE iceberg SET
                                iceberg_name = %s,
                                magnitude_value = %s,
                                magnitude_unit = %s,
                                date_time = %s
                                WHERE id = %s"""
            values = (row['title'], row['magnitude_value'], row['magnitude_unit'], row['date'], db_id)
            run_update(connection, update_iceberg, values)
            logger.info(f'Update iceberg {df_id} into iceberg table')

        else:
            create_iceberg = """INSERT INTO iceberg
                        (eonet_id ,iceberg_name, magnitude_value, magnitude_unit, date_time)
                        VALUES
                        (%s, %s, %s, %s, %s)"""
            values = (df_id, row['title'], row['magnitude_value'], row['magnitude_unit'], row['date'])
            run_update(connection, create_iceberg, values)
            logger.info(f'Insert iceberg {df_id} into iceberg table')


if __name__ == '__main__':
    table_data = pd.read_csv('/home/emuna/Documents/Itc/DM_EQ/earthquake_clean.csv')
    connection = get_connection('earthquake')
    run_query(connection, 'SHOW tables;')
    run_query(connection, 'DESCRIBE eq_cities;')
    run_query(connection, 'DESCRIBE cities;')
    run_query(connection, 'DESCRIBE earthquakes;')
    for _, row in table_data.iterrows():
        update_database(row, connection)
