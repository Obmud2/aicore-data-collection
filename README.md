# Data Collection Project
AICore

Project to collect price, mileage, location and age data from Autotrader to estimate the market trends for 2-seater sports cars.

## Milestone 1: Finding individual listing entries and URLs
Initial build of the scraper, used to accept cookies, search for a car make and model, and extract summary data of each car including the web address for each item.

Selenium is used as the main technology using a safari web driver to enable flexible website navigation and data extraction.

Technologies used:
- Conda
- Selenium

## Milestone 2: Adding further data from individual pages and storing data locally
Scrapes the list of URLs and individual page data to create dictionaries for each vehicle entry. Data and images are saved locally, as json and jpg formats respectively. Each vehicle entry is recorded with a unique id from autotrader, and a unique UUID.

Code structure is improved with increased encapsulation of internal page scraping methods, and greater abstraction to support readibility.

Technologies used:
- UUID
- JSON
- urllib
- pandas (for easy visualisation of data whilst testing code)