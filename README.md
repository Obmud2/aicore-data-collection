# Data Collection Project
AICore

Project to collect price, mileage, location and age data from Autotrader to estimate the market trends for 2-seater sports cars.

## Milestone 1: Finding individual listing entries and URLs
Initial build of the scraper, used to accept cookies, search for a car make and model, and extract summary data of each car including the web address for each item.

Selenium is used as the main technology using a safari web driver to enable flexible website navigation and data extraction.

Technologies used:
- Conda (virtual environments)
- Selenium (browser driver for completing complex web scraping beyond html)

## Milestone 2: Adding further data from individual pages and storing data locally
Scrapes the list of URLs and individual page data to create dictionaries for each vehicle entry. Data and images are saved locally, as json and jpg formats respectively. Each vehicle entry is recorded with a unique id from autotrader, and a unique UUID.

Code structure is improved with increased encapsulation of internal page scraping methods, and greater abstraction to support readibility.

Technologies used:
- UUID (unique ID generator)
- JSON (JSON file read/write)
- urllib (retrieve files from urls)
- pandas (for easy visualisation of data whilst testing code)

## Milestone 3: Documentation and Testing
Test cases are added to the scraper to check the public methods in the scraper class. Testing can be run according to the testing module.
`python -m test.test_autotrader_scraper`

Tests are run outside of the main file structure, and raw data is downloaded in the testing area. The testing is designed to check at a functional level:
- Successful initialisation of browser driver
- Successful navigation to search results and item pages
- Successful data scrape of results page and item pages
- Completeness of the scraper output
- Data output file structure according to scraper outpu
- Runtimes of the modules

Several issues were identified and resolved during testing, including:
- Inefficient detection of ads listing, solved by changing the scraping terms to more specific
- Scraper did not scrape all pages, solved by altering structure of storing scraped data
- Readability of the code was improved with docstrings and variable names

Technologies used:
- Beautiful soup (faster implementation than selenium to support faster testing)
- Regex (text matching of test cases)
- os (file navigation in python)