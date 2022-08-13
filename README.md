# Strongman Webscraper
The Strongman Webscraper is a simple Python interface to scrape data from strongman competition from the archives and prepare them in a Pandas dataframe for analysis.. This scrapes all competition data with the minimum granularity being on competitor level. The website's html is quite inelegant and consequently the webscraper is riddled with edge cases and switch cases.

## Installation Instructions
Clone the repository
```sh
git clone https://github.com/MayteSteeghs/strongman-webscraper
```

Navitage to the repository
```sh
cd /path/to/repository
```

Install required packages
```sh
py -m pip install -r requirements.txt
```

Run Application
```sh
py -m main.py
```
