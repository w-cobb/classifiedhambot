import requests
from bs4 import BeautifulSoup


URL = "https://swap.qth.com/all.php"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

page = requests.get(URL, headers=headers)
print(page.status_code)

soup = BeautifulSoup(page.content, "html.parser")

container = soup.find("div", class_="qth-content-wrap")
products = container.find_all("b")

for product in products:
    print(product)

# for product in products:
#     name = product.find("h2").text
#     link = product.find("a")['href']
#     print(name, link)