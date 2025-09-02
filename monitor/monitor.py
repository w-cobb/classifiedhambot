from bs4 import BeautifulSoup
from dotenv import load_dotenv
import email
import imaplib
import json
import logging
import os
import re
import requests
import time
from urllib.parse import quote_plus

load_dotenv()
email_address = os.getenv("EMAIL")
email_pass = os.getenv("PASSWORD")
site = os.getenv("SITE").lower()

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

API_URL = 'http://api:8000'

# Read contents of JSON file
scraping_data = None
with open('endpoints.json', 'r') as file:
    scraping_data = json.load(file)

# Get new listings from QTH
def get_new_listings_qth():
    # url = scraping_data["sites"]["qth"]["baseurl"] + scraping_data["sites"]["qth"]["listings"]
    url = 'https://swap.qth.com/all.php'
    listings_to_add = []
    
    logger.info("Searching QTH for new listings")
    
    # Get listings from first 5 pages
    for page in range(1,16):
        if page != 1:
            url = f'https://swap.qth.com/all.php?page={page}'
        page = requests.get(url, headers=headers)
        if page.status_code != 200:
            # Ran into an issue, should probably log it
            logger.error("QTH responded with status code {page.status_code}")
            return
        
        # Page returned fine, soup it up
        soup = BeautifulSoup(page.content, "html.parser")

        # This is the place where all the listings are stored
        container = soup.find("div", class_="qth-content-wrap")
        
        # To find the listing ID we need to look for the <i> tag
        listings = container.find_all("i")
        ids = []
        for item in listings:
            if "Listing #" in item.find("font").text.strip(): 
                ids.append(item.find("font").text.strip())

        # Each listing has a <b> tagg with some text
        products = container.find_all("b")
        
        # Only use <b> tags that contain product info
        filtered_products = [x for x in products if ' - ' in x.text]
        
        for i, p in zip(ids, filtered_products):
            # Get listing number for URL
            listing_num = i.split('-')[0].strip('Listing #')
            item_name = re.sub(r"fs|\bfor\s+sale\b|:*","",p.text.strip().split(' - ', 1)[1], flags=re.IGNORECASE).strip()
            listings_to_add.append([listing_num, item_name])
        
        time.sleep(1)

    # Send them to the database
    for listing in listings_to_add:
        iurl = f'https://swap.qth.com/view_ad.php?counter={listing[0]}'
        iname = listing[1]
        print(iname, ' | ', iurl)
        requests.post(f'{API_URL}/listings?iurl={iurl}&iname={quote_plus(iname)}')

# Get new listings from HamEstate
def get_new_listings_hamestate():
    base_url = 'https://www.hamestate.com/product-category/ham_equipment/'
    
    logger.info("Search HamEstate for new listings")
    
    for category in scraping_data['sites']['hamestate']['categories']:
        url = base_url + category
        end_of_pages = False
        page_num = 1
        
        # Go unto we reach the end of the pages
        while not end_of_pages:
            if page_num == 1:
                page = requests.get(url+'?orderby=date', headers=headers)
            else:
                page = requests.get(url+f'/page/{page_num}/?orderby=date', headers=headers)
            if page.status_code != 200:
                logger.error("HamEstate responded with status code {page.status_code}")
                
            # The page responded fine
            soup = BeautifulSoup(page.content, "html.parser")
            
            # We reached the end of the listings for this category
            if soup.find_All("h1",class_='not-found-title'):
                end_of_pages = True
                break
            
            # Get all prodcts from the page
            products = soup.find_all("li", class_='product')
            
            # Parse the products to get the url parameters for iurl and iname
            for product in products:
                name = product.find("h2").text
                link = product.find("a")['href']
                
                # Send this listing to the db
                requests.post(f'{API_URL}/listings?iurl={link}&iname={quote_plus(name)}')
                
            # Move on
            page_num += 1
            time.sleep(0.5)
            
    
    # for product in products:
#     name = product.find("h2").text
#     link = product.find("a")['href']
#     print(name, link)
    pass

# Parse all unread emails from QRZ
def get_new_listings_qrz():
    logger.info("Searching QRZ for new listings")
    
    new_listings = []
    with imaplib.IMAP4_SSL('imap.gmail.com') as mail:
        mail.login(email_address, email_pass)
        mail.select('inbox')
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        if not email_ids:
            logger.info('No unread emails found')
            return
        
        for eid in email_ids:
            status, message = mail.fetch(eid, '(RFC822)')
            raw = message[0][1]
            msg = email.message_from_bytes(raw)
            iname = ''
            iurl = ''
            if ' - ' in msg.get('Subject'):
                iname = msg.get('Subject').split(' - ')[1]
            else:
                continue
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get_content_disposition())
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        lines = body.split('\n')
                        for line in lines:
                            if 'forums.qrz.com/index.php?threads' in line:
                                iurl = line.replace('\r','')
            if iname and iurl:
                new_listings.append({'iname': iname, 'iurl': iurl})
    if new_listings:
        logger.info(f'Found {len(new_listings)} new listings from QRZ')
        for listing in new_listings:
            requests.post(f'{API_URL}/listings?iname={quote_plus(listing['iname'])}&iurl={quote_plus(listing['iurl'])}')
        

if __name__ == "__main__":
    # run code here
    match site:
        case "qrz":
            get_new_listings_qrz()
        case "qth":
            get_new_listings_qth()
        case "he":
            get_new_listings_hamestate()
        case _:
            logger.error("No site specifier given. Please make sure environment variable \"SITE\" is set to QRZ, QTH, or HE.")