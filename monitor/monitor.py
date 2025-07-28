import json
import logging
import requests
from bs4 import BeautifulSoup

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename="monitor.log", encoding="utf-8", 
                    format="%(asctime)s %(levelname)-8s: %(message)s", 
                    datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

# Web scraping parameters
url = ""
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

# Read contents of JSON file
scraping_data = None
with open('monitor/endpoints.json', 'r') as file:
    scraping_data = json.load(file)

# Get new listings from QTH
def get_new_listings_qth():
    url = scraping_data["sites"]["qth"]["baseurl"]

    page = requests.get(url, headers=headers)
    
    if page.status_code != 200:
        # Ran into an issue, should probably log it
        logger.error("QTH responded with status code {page.status_code}")
        return
    
    # Page returned fine, soup it up
    soup = BeautifulSoup(page.content, "html.parser")

    # This is the place where all the listings are stored
    container = soup.find("div", class_="qth-content-wrap")
    
    # Each listing has a <b> tagg with some text
    products = container.find_all("b")
    
    # To find the listing ID we need to look for the <i> tag
    listings = container.find_all("i")
    
    new_listings = []
    
    for item in listings:
        print(item.find("font").text.strip())

    for product in products:
        print(product.text.strip().split(" - "))

def get_new_listings_hamestate():
    
    # for product in products:
#     name = product.find("h2").text
#     link = product.find("a")['href']
#     print(name, link)
    pass
    

def get_new_listings_qrz():
    pass

if __name__ == "__main__":
    # run code here
    get_new_listings_qth()
    