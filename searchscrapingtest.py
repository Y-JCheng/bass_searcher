from bs4 import BeautifulSoup
import requests
import json

baseurl = "https://en.wikipedia.org"
url = "https://en.wikipedia.org/wiki/List_of_guitar_manufacturers"
response = requests.get(url).text
soup = BeautifulSoup(response, 'html.parser')
brand_link = {}
results = soup.find('div', class_="div-col columns column-width").find_all('li')
for brand in results:
    brand_name = brand.find('a').text
    brandURL = brand.find('a')['href']
    brand_link[brand_name] = baseurl + brandURL

print(brand_link)
