import requests
from bs4 import BeautifulSoup


URL = "https://www.hamestate.com/"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

print(soup)