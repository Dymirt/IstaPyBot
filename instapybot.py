import logging
from pprint import pprint
from datetime import datetime
import json
from typing import BinaryIO
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import lxml
import pickle
import re

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

USERNAME = ''
PASSWORD = ''
COOKIES_FILE = f"{USERNAME}_cookies.pkl"
BASE_URL = 'https://www.instagram.com/'

LIKE_BUTTON_ARIA_LABEL = ['Нравится', 'Like']
SLEEP_TIME = 5


class Instagram(webdriver.Firefox):
    def __init__(self, base_url, username, password):
        super().__init__()
        self.base_url = base_url
        self.username = username
        self.password = password
        self.like_button_aria_label = LIKE_BUTTON_ARIA_LABEL

    def get_posts_link(self, ig_user: str) -> list:
        self.get(f'{self.base_url}{ig_user}')
        time.sleep(SLEEP_TIME)
        page_links = self.find_elements(by=By.TAG_NAME, value='a')
        posts_links = [link.get_attribute('href') for link in page_links if '/p/' in link.get_attribute('href')]
        return posts_links

    def login(self):
        self.get(f'{self.base_url}accounts/login/')
        self.accept_cookies()
        time.sleep(SLEEP_TIME)
        self.find_element(By.NAME, value='username').send_keys(self.username)
        self.find_element(By.NAME, value='password').send_keys(self.password)
        time.sleep(SLEEP_TIME)
        self.find_elements(By.TAG_NAME, value='button')[1].click()
        time.sleep(SLEEP_TIME)

    def accept_cookies(self):
        h2_tags = self.find_elements(by=By.TAG_NAME, value='h2')
        for tag in h2_tags:
            if 'cookie' in tag.text:
                buttons = self.find_elements(by=By.TAG_NAME, value='button')
                buttons[-2].click()

    def like(self, post_link: str) -> None:
        self.get(post_link)
        time.sleep(SLEEP_TIME)
        buttons = self.find_elements(By.TAG_NAME, value='button')
        for button in buttons:
            try:
                svg = button.find_element(By.TAG_NAME, value='svg')
            except NoSuchElementException:
                continue
            if svg.get_attribute('aria-label') in self.like_button_aria_label:
                button.click()

    def liked_by(self, post_link: str) -> list:
        self.get(post_link)
        time.sleep(SLEEP_TIME)
        buttons = self.find_elements(By.TAG_NAME, value='a')
        for button in buttons:
            if 'liked_by' in button.get_attribute('href'):
                try:
                    button.click()
                except ElementClickInterceptedException:
                    # button.click() works just fine but for some reason exception appear
                    pass

        time.sleep(SLEEP_TIME)
        profile_links = set()
        page_links = self.find_elements(by=By.TAG_NAME, value='a')
        for link in page_links:
            raw_search_string = r"\b" + 'https://www.instagram.com/' + r"(\w+)/"
            if re.fullmatch(raw_search_string, link.get_attribute('href')):
                profile_links.add(link.get_attribute('href'))
        print(profile_links)



        """       links = self.find_elements(By.CLASS_NAME, value='notranslate')

        link_list = list(set([x.get_attribute('title') for x in links]))

        divs = self.find_elements(By.TAG_NAME, value='div')

        dialog = ''  # Initiate only for pep 8
        for div in divs:
            if div.get_attribute('aria-labelledby'):
                dialog = div
                try:
                    div.click()
                except ElementClickInterceptedException:
                    # button.click() works just fine but for some reason exception appear
                    pass
        #for x in range(2):
        #    dialog.send_keys(Keys.PAGE_DOWN)"""
        """            links = self.find_elements(By.CLASS_NAME, value='notranslate')
            for link in links:
                if link.get_attribute('title') not in link_list:
                    link_list"""
        #return link_list


browser = Instagram(BASE_URL, USERNAME, PASSWORD)
browser.get(f'{BASE_URL}{USERNAME}')
time.sleep(SLEEP_TIME)

try:
    cookies = pickle.load(open(COOKIES_FILE, "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)
except FileNotFoundError:
    browser.login()
    pickle.dump(browser.get_cookies(), open(COOKIES_FILE, "wb"))

browser.liked_by('https://www.instagram.com/p/CjwF6sqqE1x/')

# Save cookies at the end
pickle.dump(browser.get_cookies(), open(COOKIES_FILE, "wb"))