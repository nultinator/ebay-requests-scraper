import os
import csv
import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import concurrent.futures
from dataclasses import dataclass, field, fields, asdict

API_KEY = ""

with open("config.json", "r") as config_file:
    config = json.load(config_file)
    API_KEY = config["api_key"]


## Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_search_results(keyword, location, page_number, retries=3):
    formatted_keyword = keyword.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword}&_pgn={page_number}"
    tries = 0
    success = False
    
    while tries <= retries and not success:
        try:
            response = requests.get(url)
            logger.info(f"Recieved [{response.status_code}] from: {url}")
            if response.status_code == 200:
                success = True
            
            else:
                raise Exception(f"Failed request, Status Code {response.status_code}")
                
                ## Extract Data

            soup = BeautifulSoup(response.text, "html.parser")

            main_holder = soup.select_one("div[id='srp-river-results']")
            
            div_cards = main_holder.select("div[class='s-item__info clearfix']")


            for div_card in div_cards:
                name = div_card.select_one("div[class='s-item__title']").text
                link = div_card.select_one("a").get("href")
                price = div_card.select_one("span[class='s-item__price']").text.replace("$", "").replace(",", "")

                buy_it_now = False
                buy_it_now_tag = div_card.select_one("span[class='s-item__dynamic s-item__formatBuyItNow']")
                if buy_it_now_tag:
                    buy_it_now = True

                is_auction = False
                auction_end = None
                auction_ends_tag = div_card.select_one("span[class='s-item__time-end']")
                if auction_ends_tag:
                    is_auction = True
                    auction_ends_tag.text
                
                search_data = {
                    "name": name,
                    "url": url,
                    "price": price,
                    "buy_it_now": buy_it_now,
                    "is_auction": is_auction,
                    "auction_end": auction_end
                }
                print(search_data)

            logger.info(f"Successfully parsed data from: {url}")
            success = True
        
                    
        except Exception as e:
            logger.error(f"An error occurred while processing page {url}: {e}")
            logger.info(f"Retrying request for page: {url}, retries left {retries-tries}")
    if not success:
        raise Exception(f"Max Retries exceeded: {retries}")




def start_scrape(keyword, pages, location, retries=3):
    for page in range(pages):
        scrape_search_results(keyword, location, page, retries=retries)



if __name__ == "__main__":

    MAX_RETRIES = 3
    MAX_THREADS = 5
    PAGES = 1
    LOCATION = "us"

    logger.info(f"Crawl starting...")

    ## INPUT ---> List of keywords to scrape
    keyword_list = ["gpu"]
    aggregate_files = []

    ## Job Processes
    for keyword in keyword_list:
        filename = keyword.replace(" ", "-")

        start_scrape(keyword, PAGES, LOCATION, retries=MAX_RETRIES)
        
    logger.info(f"Crawl complete.")
