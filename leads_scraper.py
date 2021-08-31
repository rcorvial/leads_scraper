# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 22:59:14 2021

@author: Rafael Corvillo
"""

import time
import random
import os.path
import argparse
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import ElementNotInteractableException, \
     ElementClickInterceptedException


class Scraper:
    """
    Class to scrape leads from Google Maps using a URL with the search and
    the location.
    """

    def __init__(self):
        """
        Scraper initialization: Initialize Webdriver and its options.
        """
        # Path to the browser executable
        self.exec_path = "chromedriver.exe"

        # Add additional Options to the Webdriver
        self.options = ChromeOptions()
        #self.options.add_argument("--headless")

        # Initialize Webdriver
        self.driver = webdriver.Chrome(executable_path=self.exec_path,
                                       options=self.options)

        # Initialize Webdriver timeout to 10 seconds
        self.wait = WebDriverWait(self.driver, 10)


    def _close_session(self):
        """
        Private method to close Webdriver session
        """
        self.driver.close()


    def _get_urls(self, search_url):
        """
        Private method to open a search URL and extract the shops URLs from
        the Google Maps results.

        :param str search_url: URL to the Google Maps search results
        :return list: List with the shops URLs
        """
        urls_list = []

        # Opening the search URL
        self.driver.get(search_url)

        # Maximize window
        self.driver.maximize_window()

        # Accept cookies
        try:
            accept_button = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]\
                /form/div[1]/div/button"
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, accept_button))).click()
        except ElementClickInterceptedException as e:
            print("Error: {}".format(e))
            return

        # Wait until shops section is loaded plus 1-2 seconds
        shops_box = "//*[@id='pane']/div/div[1]/div/div/div[4]/div[1]/div"
        self.wait.until(EC.presence_of_element_located((By.XPATH, shops_box)))
        time.sleep(random.uniform(1, 2))

        # Loop over the shops to get the URLs
        empty_page = False
        while True:
            # Get visible shops in the current page
            shops = self.driver.find_elements_by_xpath(shops_box)
            num_shops = len(shops)

            # Loop over the shops in current page
            while len(shops) < 40:
                # Scroll to the last shop loaded
                try:
                    ActionChains(self.driver).move_to_element(shops[-1]).\
                        perform()
                except ElementNotInteractableException :
                    print("There are no more shops in current page")
                    break

                # Wait until the next shops are loaded and get them
                next_shops = "//*[@id='pane']/div/div[1]/div/div/div[4]/div[1]\
                    /div[{}]".format(num_shops+1)
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, next_shops)))
                shops = self.driver.find_elements_by_xpath(shops_box)

                # Corner case: last page with no shops
                if num_shops == len(shops):
                    print("There are no shops in the last page")
                    empty_page = True
                    break
                num_shops = len(shops)

            # Extract the URL list from current page
            i = 1
            while i < num_shops:
                path = "//*[@id='pane']/div/div[1]/div/div/div[4]/div[1]/\
                    div[{}]/div/a".format(i)
                shop_url = self.driver.find_element_by_xpath(path).\
                    get_attribute('href')
                urls_list.append(shop_url)
                i += 2

            # If the button to go to the next page is disabled, then current
            # page is the last page
            next_button_disabled = \
                self.driver.find_element_by_id('ppdPk-Ej1Yeb-LgbsSe-tJiF1e').\
                    get_attribute('disabled')
            if next_button_disabled or empty_page:
                break

            # Go to the next page
            self.wait.until(
                EC.invisibility_of_element((By.CLASS_NAME,
                                            'qq71r-qrlFte-bF1uUb')))
            self.wait.until(
                EC.element_to_be_clickable((By.ID,
                                            'ppdPk-Ej1Yeb-LgbsSe-tJiF1e'))).\
                click()

            # Wait until next page is loaded
            time.sleep(random.uniform(3, 4))

        return urls_list


    def _get_url_content(self, url):
        """
        Open shop URL and extract its information.

        :param str url: URL to the information of the shop
        :return str: HTML content of the shop URL
        """
        # Opening the search URL
        self.driver.get(url)

        # Wait until page is loaded
        time.sleep(random.uniform(3, 4))

        return self.driver.page_source


    def get_leads_info(self, search_url):
        """
        Get a dictionary of dictionaries with the information of the leads
        extracted from the shops URLs obtained from Google Maps results.

        :param str search_url: URL to the Google Maps results.
        :return: dict: Dictionary with the information of the leads
        """
        # Get leads URL to extract the information
        leads_url = self._get_urls(search_url)

        # Dictionary to store all the information obtained from the URLs
        leads_dict = dict()

        # Index to store the leads
        index = 0

        # Loop each URL to get leads information
        for url in leads_url:
            # Create an empty dictionary to store the information
            leads_dict[index] = dict()

            print("\nScraping lead {}".format(index))
            page = self._get_url_content(url)

            # Get the HTML content
            page_content = BeautifulSoup(page, 'html.parser')

            # Get the information of the movie from the HTML
            name_class = 'x3AX1-LfntMc-header-title-title'
            leads_dict[index]['name'] = \
                page_content.find('h1', {'class': name_class}).get_text().strip()
            print("Lead: {}".format(leads_dict[index]['name']))

            category = page_content.find('button', {'jsaction': 'pane.rating.category'})
            leads_dict[index]['category'] = category.get_text().strip() \
                if category else ''

            review = page_content.find('button', {'jsaction': 'pane.rating.moreReviews'})
            leads_dict[index]['reviews'] = review.get_text().strip().split()[0] \
                if review else ''

            rating = page_content.find('span', {'class': 'aMPvhf-fI6EEc-KVuj8d'})
            leads_dict[index]['rating'] = rating.get_text().strip() \
                if rating else '0'

            address = page_content.find('button', {'data-item-id': 'address'})
            leads_dict[index]['address'] = address.get_text().strip() \
                if address else ''

            web = page_content.find('button', {'data-item-id': 'authority'})
            leads_dict[index]['web'] = web.get_text().strip() if web else ''

            # data-tooltip attribute depends on the locale. For example, if
            # the language is configured in English, the attribute
            # "Copiar el número de teléfono" must be changed by
            # "Copy phone number".
            phone = page_content.find('button', {'data-tooltip': "Copiar el número de teléfono"})
            leads_dict[index]['phone'] =  phone.get_text().strip() \
                if phone else ''

            leads_dict[index]['google_maps'] = url

            # Next lead
            index += 1

            # Wait 1 second for the next HTTP request
            time.sleep(1)

        # Close Webdriver
        self._close_session()
        
        return leads_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Leads scraper from Google Maps')
    parser.add_argument('-s', '--search', type=str, nargs='*',
                        help='Type of lead to search')
    parser.add_argument('-l', '--location', type=str, nargs='*',
                        help='Location to look for shops')
    args = parser.parse_args()
    
    if args.search:
        search = '+'.join(args.search)
    if args.location:
        location = '+'.join(args.location)

    print("Searching \"{}\" in \"{}\"".format(' '.join(args.search),
                                              ' '.join(args.location)))
    search_url = "https://www.google.com/maps/search/{}+{}"\
        .format(search, location)
    print("URL: {}".format(search_url))
    scraper = Scraper()
    leads_dict = scraper.get_leads_info(search_url)

    # Write CSV file with the dataframe generated
    leads_df = pd.DataFrame.from_dict(leads_dict, orient="index")
    if os.path.isfile('leads.csv'):
        leads_df.to_csv('leads.csv', mode='a', encoding='utf-8-sig', header=False)
    else:
        leads_df.to_csv('leads.csv', encoding='utf-8-sig')

    print("\nDataset created")