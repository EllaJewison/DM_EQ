
# Earthquake Data Mining Project :volcano:

##  Description
This is a program for scraping updated information about earthquakes from the website: 
[earthquakes](https://www.allquakes.com/earthquakes/today.html). 

The scraping  done in two steps: 
1. Collect the data from the main page contains the most recent quakes of magnitude 3.6 or higher.
That includes an important data of each quake - date, magnitude, location etc, and a link to a page with more information about the quake.
2. Collect the data from each earthquake link for more detailed information. This information includes 
nearby towns and cities, weather, numbers of reports, etc.

To show the progress, the program prints to standard output the current earthquake
number that is its data is now collected. Once all the data is collected, print first the data from the main page, and then the more detailed data for each quake.

## Instructions

Clone and run the scraper on this website "https://www.allquakes.com/earthquakes/today.html". 
This scraper will provide you with information from the main page. The first table returned will have the following information:
- date and time
- location
- magnitude
- detail

You will be provoded also with a more detail table for each earthquake. This table will contrain the following information :  
- date and time
- location
- status
- depth
- magniture
- antipode
- epicenter latitude and longitude
- nearest volcano
- nearby towns and city
- felt (number of report on feeling the shake)
- weather at the epicenter
- estimated seismic energy release


p.s. make sur you install the requirements.txt

enjoy


## What is Next
The next step is to create a CLI for the user to get specific earthquake information, and store all the collected data in a data frame for better access.

# URL links in the table EQ

[scrap_from_p2(quake_id, quake_url)
](https://linktodocumentation)
#scrapper for each EQ

[main_scrapper_p1()
](https://linktodocumentation)
#scapes main table then gets the url link "more" and then scrpas it builds_table_show_more


## Authors

- [@EllaJewison , @Sassaraf ,@emunac](https://www.github.com/octokatherine)
