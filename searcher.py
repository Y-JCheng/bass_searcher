from bs4 import BeautifulSoup
import requests
import json
import sqlite3

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

class bass():
    '''a bass

    Instance Attributes
    -------------------
    product_name: string
        name of the bass

    brand: string
        url of the theme picture for the project

    category: string
        category of the type of bass
    
    price: float
        price of the bass

    styles: list
        the styles available

    description: string
        a short description about the bass

    features: string
        the special features of the bass

    picURL: string
        a link to the image of the bass

    URL: string
        the link to the product page
    '''
    
    def __init__(self, product_name, brand, category, price, styles, description, features, picURL, URL):
        self.product_name = product_name
        self.picURL = picURL
        self.price = price
        self.description = description
        self.brand = brand
        self.styles = styles
        self.category = category
        self.features = features
        self.URL = URL

    def info(self):
        '''

        Parameters
        ----------
        None

        Returns
        ----------
        a list of basic information of the bass
        '''
        return [self.product_name, self.brand, self.category, self.price, self.styles, self.description, self.features, self.picURL, self.URL]


class brand():

    def __init__(self, brand_name, brand_country, brand_description, URL):
        self.brand_name = brand_name
        self.brand_country = brand_country
        self.brand_description = brand_description
        self.URL = URL

    def info(self):
        '''Report a list of information

        Parameters
        ----------
        None

        Returns
        ----------
        a list of basic information of a brand
        '''
        return [self.brand_name, self.brand_country, self.brand_description, self.URL]


def create_db():
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    drop_basses = 'DROP TABLE IF EXISTS "Basses"'
    drop_brands = 'DROP TABLE IF EXISTS "Brands"'
    create_basses = '''
        CREATE TABLE IF NOT EXISTS "Basses" (
            'BassId' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'ModelName' TEXT NOT NULL,
            'Brand' TEXT NOT NULL,
            'Category' INTEGER NOT NULL,
            'Price' DECIMAL NOT NULL,
            'Styles' TEXT NOT NULL,
            'Description' TEXT,
            'Features' TEXT,
            'PicURL' TEXT NOT NULL,
            'URL' TEXT NOT NULL
        )
    '''

    create_brands = '''
        CREATE TABLE IF NOT EXISTS "Brands" (
            "BrandId" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "BrandName" TEXT NOT NULL,
            "BrandCountry" TEXT,
            "BrandDescription" TEXT,
            "URL" TEXT NOT NULL
        );
    '''

    cur.execute(drop_basses)
    cur.execute(drop_brands)
    cur.execute(create_basses)
    cur.execute(create_brands)
    conn.commit()
    conn.close()


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def make_request(url):
    '''Make a request to the Web using the baseurl and params
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    
    Returns
    -------
    dict
        the data returned from making the request in the form of a dictionary
    '''
    response = requests.get(url).text
    return response


def make_request_with_cache(url):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search (i.e. “#2020election”)
    count: int
        The number of tweets to retrieve
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache JSON
    '''
    if url in CACHE_DICT.keys():
        print("Using Cache")
        return CACHE_DICT[url]
    else:
        print("Fetching", url)
        CACHE_DICT[url] = make_request(url)
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]


def get_basses():
    '''Get a list of 
    
    Parameters
    ----------
    None
    
    Returns
    -------
    instance
        a project instance
    '''
    baseurl = "https://www.guitarcenter.com"
    response = make_request_with_cache("https://www.guitarcenter.com/Bass.gc")
    soup = BeautifulSoup(response, 'html.parser')
    match = soup.find('div', class_='results-options--option -matches').var.text.replace(',','')
    bass_link = {}
    for i in range(int(int(match)/30)+1):
        newurl = "https://www.guitarcenter.com/Bass.gc?Nao=" +str(30*i)
        response = make_request_with_cache(newurl)
        newsoup = BeautifulSoup(response, 'html.parser')
        results = newsoup.find('div', id="resultsContent").find_all('div', class_="product")
        for product in results:
            product_name = product.find('div', class_='productTitle').text.strip()
            productURL = product.find('div', class_='productTitle').a['href']
            bass_link[product_name] = baseurl + productURL
        
    return bass_link


def get_bass_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a project page in indiegogo
    
    Returns
    -------
    instance
        a project instance
    '''
    response = make_request_with_cache(site_url)
    soup = BeautifulSoup(response, 'html.parser')
    if soup.find('div', class_='titleWrap') is None:
        pass
    else:
        product_name = soup.find('div', class_='titleWrap').text.lstrip()
        brand = soup.find('div', class_='titleWrap').find('span', class_='brand').text
        picURL = soup.find('div', class_='product-left').find('img')['src']
        try:
            price = float(soup.find('span', class_='topAlignedPrice').text.strip().strip('$').replace(',', ''))
        except:
            price = '0'

        try:
            description = soup.find('section', id='product-overview').find('p', class_='description').text
        except:
            description = ''
        
        styleslist = []
        styles = ''
        allstyles = soup.find('div', id='chooseStyleWrap').find_all('li')
        for style in allstyles:
            stylename = style.find('div', class_='styleLabel').text
            styleslist.append(stylename)
        styles = ', '.join(styleslist)
        if len(styleslist) < 1:
            stylename = soup.find('div', class_='titleWrap').find('span', class_='skuStyle').text
            styles = stylename
        
        try:
            category = soup.find_all('a', class_='category')[2].text
        except:
            category = soup.find_all('a', class_='category')[1].text

        try:
            uls = soup.find('div', class_='specs').find_all('ul')
            featureslist = []
            for ul in uls:
                lis = ul.find_all('li')
                for li in lis:
                    featureslist.append(li.text.strip())
            features = ' \n '.join(featureslist)
        except:
            features = ''
        return bass(product_name, brand, category, price, styles, description, features, picURL, site_url)


def get_brands():
    '''Get a list of 
    
    Parameters
    ----------
    None
    
    Returns
    -------
    instance
        a project instance
    '''
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
    return brand_link


def get_brands_instance(brandname, site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a project page in indiegogo
    
    Returns
    -------
    instance
        a project instance
    '''
    response = make_request_with_cache(site_url)
    soup = BeautifulSoup(response, 'html.parser')
    try:
        infobox = soup.find('table', class_='infobox vcard').find_all('tr')
        info_dict = {}
        website = ""
        country = ""
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
        else:
            website = site_url
    except:
        website = site_url
        country = ""

    row_description = soup.find('div', id='mw-content-text').find('div', class_='mw-parser-output').find_all('p')
    if 'coordinates' in str(row_description[0]):
        description = row_description[1].text
    else:
        description = row_description[0].text
    
    return brand(brandname, country, description, website)


def save_to_basses(bass):
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    insert_basses = '''
    INSERT INTO Basses
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cur.execute(insert_basses, bass)
    conn.commit()


def save_to_brands(brand):
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    insert_brands = '''
    INSERT INTO Brands
    VALUES (NULL, ?, ?, ?, ?)
    '''
    cur.execute(insert_brands, brand)
    conn.commit()    


if __name__ == "__main__":
    create_db()
    CACHE_DICT = open_cache()
    bass_url_dict = get_basses()
    brand_url_dict = get_brands()
    for keys,values in brand_url_dict.items():
        save_to_brands(get_brands_instance(keys, values).info())
    for keys,values in bass_url_dict.items():
        try:
            save_to_basses(get_bass_instance(values).info())
        except:
            pass
