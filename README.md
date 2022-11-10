
# Earthquake Data Mining Project

Description: of what this project does and who it's for
In thes files you will find a webscaper for the main table in "https://www.allquakes.com/earthquakes/today.html"
and the links inside table for more information 

## Instructions 
after cloning project run scraper.py to scrape and display the updated earthquakes' data.

p.s. make sur you install the requirements.txt

enjoy


## Documentation

[create_soup_from_link(link ) 
](https://linktodocumentation)
#creates soup from link 

[get_show_more_url(my_soup) 
](https://linktodocumentation)
#returns the url for full table 


[extract show more soup(my_soup) 
](https://linktodocumentation)
#returns soup object of all additional tables 


[get_date(quake_data_cells)
](https://linktodocumentation)
#return the date of the earthquake



[get_magnitude(quake_data_cells)
](https://linktodocumentation)
#return the magnitude of the earthquake


[get_depth(quake_data_cells)
](https://linktodocumentation)
#return the depth of the earthquake


[get_nearest_volcano(quake_data_cells)
](https://linktodocumentation)
#return the nearest volcano of the earthquake


[get_location(quake_data_cells)
](https://linktodocumentation)
#return the location of the earthquake


[get_details_url(quake_data_cells)
](https://linktodocumentation)
#return the details url  to show more about the earthquake


[extract_data_from_quakes(quakes)
](https://linktodocumentation)
#This will take the table and make it readable-ish


[ get_eq(soup)
](https://linktodocumentation)
#this finds all the earthquakes by magnitud


[scrap_from_p2(quake_url)
](https://linktodocumentation)
#This function takes the quake id and the url link of an earthquake, opens the "more page" and retrieves the data 

[main_scrapper_p1()
](https://linktodocumentation)
#This will scrap all the updated data and more details about each earthquake



# URL links in the table EQ

[scrap_from_p2(quake_id, quake_url)
](https://linktodocumentation)
#scrapper for each EQ

[main_scrapper_p1()
](https://linktodocumentation)
#scapes main table then gets the url link "more" and then scrpas it builds_table_show_more


## Authors

- [@EllaJewisonrine , @Sassaraf ,@emunac](https://www.github.com/octokatherine)
