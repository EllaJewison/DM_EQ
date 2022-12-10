
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


### Clone
Clone the repo on your local computer and install the needed requirements from requirements.txt

### Create the database in your computer
Run the script name.py and make sure to change the username and password on the connection function. 

### Scapping :
Run the scraper.py file from the command line interface from this website "https://www.allquakes.com/earthquakes/today.html". 
You can add argument to this command like the examples below:

Usage :
scraper.py [-h] [--date DATE]
            [--magnitude MAGNITUDE]
            [--n_rows NUMBER]
            mysql_user mysql_password

positional arguments:
  mysql_user
  mysql_password

options:
  -h, --help            show this help message and exit
  --date START_DATE END_DATE(optional) 
  --magnitude FROM_MAGNITUDE TO_MAGNITUDE(optional)
  --n_rows NUMBER

Examples:
1. scraper.py user password --date 12/11/2022 14/11/2022 -> will scrape all earthquakes from 12/11/2022 to 14/11/2022
2. scraper.py user password --date 12/11/2022 --magnitude 3.6 8.1 ->
    will scrape all earthquakes from 12/11/2022 until today that have magnitude between 3.6 to 8.1
3. scraper.py user password --date 12/11/2022 --magnitude 3.6  ->
    will srcape all earthquakes from 12/11/2022 until today
    that have magnitude above 3.6
4. scraper.py user password --magnitude 7 --n_rows 100 -> will scrape all earthquakes that have magnitude above 7
    limited to 100 first earthquakes


### What comes out ?



This scraper will update your database with information from the website. The first table returned will have the following information:
- date and time
- location
- magnitude
- detail

The database will also be updated with a more detail table for each earthquake. This table will contains the following information :  
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

See the attached ERD ERD_earthquake

### Data cleaning and converting 
For your information, the data was cleaned and converted to relevant unit before passing it on to the database. Below is a short explanation of the cleaning and converting process:

- the magnitude and depth are converted to float
- the status is turned into a boolean, True is confirmed, False otherwise,
- the coordinates of the epicentre and antipode are converted to positive and negative. Positive for North and East and Negative for South and  West.
- date & time are kept in UTC format
- the intensity of the shaking in converted into categorical number ranging from 1 (the least amont of shaking) to 4 (the most amount of shaking) 
- Felt is converted to a int of number of reports
- Estimated energy release is converted to a float
- The towns and cities are also stored with the population and the distance to the earthquake



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
