# Data Collection Project
AICore

Project to collect price, mileage, location and age data from Autotrader to estimate the market trends for 2-seater sports cars.

## Milestone 1: Finding individual listing entries and URLs
Initial build of the scraper, used to accept cookies, search for a car make and model, and extract summary data of each car including the web address for each item.

Selenium is used as the main technology using firefox web driver (geckodriver) to enable headless website navigation and data scraping.

Technologies used:
- Conda (virtual environments)
- Selenium (browser driver for completing complex web scraping beyond html)
- Chrome driver
- Geckodriver (firefox)

## Milestone 2: Adding further data from individual pages and storing data locally
Scrapes the list of URLs and individual page data to create dictionaries for each vehicle entry. Data and images are saved locally, as json and jpg formats respectively. Each vehicle entry is recorded with a unique id from autotrader, and a unique UUID.

Code structure is improved with increased encapsulation of internal page scraping methods, and greater abstraction to support readibility.

Technologies used:
- UUID (unique ID generator)
- JSON (JSON file read/write)
- urllib (retrieve files from urls)
- pandas (for easy visualisation of data whilst testing code)

## Milestone 3: Documentation and Testing
Test cases are added to the scraper to check the public methods in the scraper and vehicle data classes. Testing can be run using unittest:
`python -m unittest`

Tests are run outside of the main file structure, and raw data is downloaded in the testing area. The testing is designed to check at a functional level:
- Successful initialisation of browser driver
- Successful navigation to search results and item pages
- Successful data scrape of results page and item pages
- Completeness of the scraper output
- Data output file structure according to scraper outputs
- Runtimes of the modules

Several issues were identified and resolved during testing, including:
- Inefficient detection of ads listing, solved by changing the scraping terms to more specific
- Scraper did not scrape all pages, solved by altering structure of storing scraped data
- Readability of the code was improved with docstrings and variable names
- Testing file dependencies were identified and removed.
- Handling of deleted webpages was added
- Detection of headless mode in chrome webdriver
- ARM compatibility of chrome webdriver

Technologies used:
- Beautiful soup (faster implementation than selenium to support faster testing)
- Regex (text matching of test cases)
- os (file navigation in python)
- unittest (python testing framework)

TODO:
- Support dynamic class ids from autotrader html

## Milestone 4: Cloud Storage

Connections to AWS cloud storage are added to scalably store the data from the web scraper. Connections to the AWS webserver are handled using the AWS_handler class. Data is uploaded to RDS using batch processing.

Pandas is used to manage the database locally before uploading to RDS. This ensures that duplicate data is not re-uploaded.

Technologies used:
- AWS RDS (using sqlalchemy and psycopg2)
- AWS S3 (using boto3)
- Numpy, Pandas, SQL, SQLAlchemy, psycopg2, tqdm

## Milestone 5: Containerisation

Containerisation using Docker is introduced to add portability to the scraper. The dockerfile is used to install Firefox and geckodriver in the docker image. The docker image is uploaded to dockerhub for distribution.

Download and run the docker image using:
`docker run -d --rm obmud2/scraper:v1_amd64 "Vehicle_make" "Vehicle_model"` (for linux)
or
`docker run -d --rm obmud2/scraper:v1 "Vehicle_make" "Vehicle_model"` (for arm46)

To build and push the docker image:
`docker build --platform linux/amd64 --tag obmud2/scraper:v1_amd64 .`
`docker push obmud2/scraper:v1_amd64`

The docker image is installed on an AWS EC2 instance using a linux amd64 EC2 instance and is scheduled to run daily at 0400 using crontab scheduling. STDOUT of the docker container is recorded in `log.txt` on the EC2 instance.

Technologies used:
- Docker
- Dockerhub
- EC2
- crontab
