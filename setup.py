from setuptools import setup
from setuptools import find_packages

setup(
    name='scraper',
    version='0.0.1',
    description='Package to scrape vehicle data from Autotrader',
    url='',
    author='Jon Pring',
    license='MIT',
    test_suite='tests',
    packages=find_packages(),
    install_requires=['regex', 'tqdm', 'selenium', 'undetected_chromedriver', 
                    'boto3', 'psycopg2', 'pandas', 'sqlalchemy', 'uuid', 'bs4']
)