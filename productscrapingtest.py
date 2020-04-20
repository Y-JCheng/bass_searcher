from bs4 import BeautifulSoup
import requests
import json

response = requests.get("https://en.wikipedia.org/wiki/MotorAve").text
soup = BeautifulSoup(response, 'html.parser')
infobox = soup.find('table', class_='infobox vcard').find_all('tr')
info_dict = {}
for info in infobox:
    try:
        info_dict[info.find('th').text.lower()] = info.find('td')
    except:
        pass

if 'headquarters' in info_dict.keys():
    country = info_dict['headquarters'].find('div', class_='country-name').text
elif 'country' in info_dict.keys():
    country = info_dict['country'].text
if 'website' in info_dict.keys():
    website = info_dict['website'].a['href']

row_description = soup.find('div', id='mw-content-text').find('div', class_='mw-parser-output').find_all('p')
if 'coordinates' in str(row_description[0]):
    description = row_description[1].text
else:
    description = row_description[0].text
print(description)


# styles = []
# allstyles = soup.find('div', id='chooseStyleWrap').find_all('li')
# for style in allstyles:
#     stylename = style.find('div', class_='styleLabel').text
#     styles.append(stylename)
# if len(styles) < 1:
#     stylename = soup.find('div', class_='titleWrap').find('span', class_='skuStyle').text
#     styles.append(stylename)
# category = soup.find_all('a', class_='category')[2].text
# uls = soup.find('div', class_='specs').find_all('ul')
# features = []
# for ul in uls:
#     lis = ul.find_all('li')
#     for li in lis:
#         features.append(li.text.strip())