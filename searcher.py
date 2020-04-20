from bs4 import BeautifulSoup
import requests
import json
import sqlite3

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

class bass():
    '''a crowdfunding project

    Instance Attributes
    -------------------
    projectname: string
        the name of a crowdfunding project

    picURL: string
        the url of the theme picture for the project

    fundingstatus: string
        the status of the crowdfunding project

    description: string
        a short description for the project

    category: string
        the category of a project
    
    currentfund: int
        the amounts of money current funded

    currency: string
        the currency of the funds

    percentage: s
        the zip-code of a national site (e.g. '49931', '82190-0168')

    owner: string
        the name of the project owner
    '''
    
    def __init__(self, product_name, brand, picURL, price, description, styles, category, features):
        self.product_name = product_name
        self.picURL = picURL
        self.price = price
        self.description = description
        self.brand = brand
        self.styles = styles
        self.category = category
        self.features = features


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
            'PicURL' TEXT NOT NULL,
            'Price' DECIMAL NOT NULL,
            'Description' TEXT NOT NULL,
            'Styles' TEXT NOT NULL,
            'Category' INTEGER NOT NULL,
            'features' TEXT
        )
    '''

    create_brands = '''
        CREATE TABLE IF NOT EXISTS "Brands" (
            "BrandId" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "BrandName" TEXT NOT NULL,
            "BrandDescription" TEXT,
            "BrandCountry" TEXT,
            "BrandLink" TEXT
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
            bass_link[product_name] = productURL
        
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
    product_name = soup.find('div', class_='titleWrap').text
    brand = soup.find('div', class_='titleWrap').find('span', class_='brand').text
    picURL = soup.find('div', class_='product-left').find('img')['src']
    price = soup.find('span', class_='topAlignedPrice').text.strip().strip('$')
    description = soup.find('section', id='product-overview').find('p', class_='description').text
    styles = []
    allstyles = soup.find('div', id='chooseStyleWrap').find_all('li')
    for style in allstyles:
        stylename = style.find('div', class_='styleLabel').text
        styles.append(stylename)
    if len(styles) < 1:
        stylename = soup.find('div', class_='titleWrap').find('span', class_='skuStyle').text
        styles.append(stylename)
    category = soup.find_all('a', class_='category')[2].text
    uls = soup.find('div', class_='specs').find_all('ul')
    features = []
    for ul in uls:
        lis = ul.find_all('li')
        for li in lis:
            features.append(li.text.strip())
    return bass(product_name, brand, picURL, price, description, styles, category, features)


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
    results = soup.find('div', class_="mw-parser-output").find_all('li')
    for brand in results:
        brand_name = brand.find('a').text
        brandURL = brand.find('a')['href']
        brand_link[brand_name] = baseurl + brandURL
    return brand_link


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    bass_url_dict = get_basses()
    get_move = input('Enter a search keywords, or "exit" \n: ')
    if get_move.lower() == "exit":
        print("Bye")
    elif get_move.lower() in bass_url_dict.keys():
        print("hi!")