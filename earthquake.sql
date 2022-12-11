
DROP DATABASE IF EXISTS  earthquake;
CREATE DATABASE earthquake;
USE earthquake;


CREATE TABLE IF NOT EXISTS earthquakes(id INT AUTO_INCREMENT PRIMARY KEY,
                                                         link_id INT,
                                                         date_time VARCHAR(255), 
                                                         local_time_at_epicenter VARCHAR(255), 
                                                         status BOOL,
                                                         magnitude FLOAT,
                                                         depth FLOAT,
                                                         epicenter_latitude_longitude VARCHAR(255),
                                                         antipode VARCHAR(255),
                                                         shaking_intensity INT,
                                                         felt INT,
                                                         primary_data_source VARCHAR(255),
                                                         nearest_volcano VARCHAR(255),
                                                         estimated_seismic_energy VARCHAR(255)
                                                         );

CREATE TABLE IF NOT EXISTS eq_cities( id INT AUTO_INCREMENT PRIMARY KEY ,
                                                        eq_id INT,
                                                        city_id INT, 
                                                        distance float
                                                        );

CREATE TABLE IF NOT EXISTS cities( id INT AUTO_INCREMENT PRIMARY KEY ,
                                                    city_name VARCHAR(255),
                                                    population INT
                                                     );
                                                     

CREATE TABLE IF NOT EXISTS fire(id INT AUTO_INCREMENT PRIMARY KEY ,
                                                    eonet_id INT,
                                                    fire_name VARCHAR(255),
                                                    latitude FLOAT,
                                                    longitude FLOAT,
                                                    date_time DATE
                                                    );

CREATE TABLE IF NOT EXISTS iceberg(id INT AUTO_INCREMENT PRIMARY KEY,
                                                    eonet_id INT,
                                                    magnitude_value FLOAT,
                                                    magnitude_unit VARCHAR(255),
                                                    date_time DATE
                                                    );

CREATE TABLE IF NOT EXISTS volcano( id INT AUTO_INCREMENT PRIMARY KEY ,
                                                    eonet_id INT,
                                                    volcano_name VARCHAR(255),
                                                    latitude FLOAT,
                                                    longitude FLOAT,
                                                    date_time DATE
                                                    );