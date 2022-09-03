import requests
from bs4 import BeautifulSoup

from selenium import webdriver 
from selenium.webdriver.common.by import By
driver = webdriver.Safari()
driver.get('https://www.zoopla.co.uk/to-rent/')
i = driver.find_element(by=By.XPATH, value='//button')
driver.close()

for el in i:
    print(i)

# url = "https://en.wikipedia.org/wiki/Python_(programming_language)"

# page = requests.get(url)
# html = page.text
# soup = BeautifulSoup(html, 'html.parser')

# methods = soup.find(name='span', attrs={'id':'Methods'})
# next_en = methods.find_parent().find_next_sibling()
# print(next_en.text)