import logging
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

username = ''
password = ''

BASE_URL = 'https://www.instagram.com/'


class Instagram(webdriver.Firefox):
    def __init__(self, base_url, username, password):
        super().__init__()
        self.base_url = base_url
        self.username = username
        self.password = password
        self.wait = WebDriverWait(self, 5)
        self.implicitly_wait(5)

    def get_posts_link(self, ig_user: str) -> list:
        self.get(f'{self.base_url}{ig_user}')
        page_links = self.find_elements(by=By.TAG_NAME, value='a')
        posts_links = [link.get_attribute('href') for link in page_links if '/p/' in link.get_attribute('href')]
        return posts_links

    def login(self):
        self.get(f'{self.base_url}accounts/login/')
        self.accept_cookies()
        self.find_element(By.NAME, value='username').send_keys(self.username)
        self.find_element(By.NAME, value='password').send_keys(self.password)
        time.sleep(5)
        self.find_elements(By.TAG_NAME, value='button')[1].click()
        time.sleep(5)

    def accept_cookies(self):
        h2_tags = self.find_elements(by=By.TAG_NAME, value='h2')
        for tag in h2_tags:
            if 'cookie' in tag.text:
                buttons = self.find_elements(by=By.TAG_NAME, value='button')
                buttons[-2].click()


browser = Instagram(BASE_URL, username, password)
browser.login()

DONORS = ['kwieciepaproci', 'moni_ziel']

for donor in DONORS:
    print(browser.get_posts_link(donor))