# Introduction

In my opinion, this project is a very interesting tool for those who are immersed in the world of entrepreneurship and are looking for future customers (leads).

With this tool you can scrape the results of Google Maps and extract the information about the businesses that interest you. You just have to indicate the words to search and the location where you want to look for your leads.

## Requirements

This project is developed using Python so you can install the requirements to run the script using the _requirements.txt_ file in your local environment or in a virtual environment.

```
pip install -r requirements.txt
```

Another requirement is to download the Chrome driver version equal than your Chrome browser version. You can download it from https://chromedriver.chromium.org/downloads. Save the driver in the same folder with name _chromedriver.exe_ (default name).


## Script execution

To show the usage of the script you have to run the following command:

```
python leads_scraper.py --help
```

and the output will be the following:

```
usage: leads_scraper.py [-h] [-s [SEARCH [SEARCH ...]]] [-l [LOCATION [LOCATION ...]]]

Leads scraper from Google Maps

optional arguments:
  -h, --help            show this help message and exit
  -s [SEARCH [SEARCH ...]], --search [SEARCH [SEARCH ...]]
                        Type of lead to search
  -l [LOCATION [LOCATION ...]], --location [LOCATION [LOCATION ...]]
                        Location to look for shops
```

Then, and example of execution would be the following:

```
python leads_scraper.py -s italian restaurant -l London
```

This command will search in Google Maps the italian restaurants in London and extract the links to all results. After that, it will go to every link and extract the information about the business.