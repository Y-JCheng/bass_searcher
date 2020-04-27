from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import collections
import plotly
import plotly.graph_objects as go
from flask import Flask, render_template, request
import APIkey

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}
API_KEY = APIkey.YOUTUBE_API_KEY
app = Flask(__name__)

# The first two parts are used to define classes for basses and brands when scrapping
class bass():
    '''A bass

    Instance Attributes
    -------------------
    product_name: string 
        Name of the bass

    brand: int
        The brand's id of the bass

    other_brand: string
        The brand's name of the bass if the brand is not in the brands list

    category: string
        The type of the bass
    
    price: float
        The price of the bass

    styles: list
        The styles of the bass

    description: string
        A short description about bass

    features: string
        The special features of the bass

    picURL: string
        A link to the image of the bass

    URL: string
        A link to the product page
    '''
    
    def __init__(self, product_name, brand, other_brand, category, price, styles, description, features, picURL, URL):
        self.product_name = product_name
        self.picURL = picURL
        self.price = price
        self.description = description
        self.brand = brand
        self.other_brand = other_brand
        self.styles = styles
        self.category = category
        self.features = features
        self.URL = URL

    def info(self):
        '''Report a list of basic information of the bass

        Parameters
        ----------
        None

        Returns
        ----------
        A list of basic information of the bass
        '''
        return [self.product_name, self.brand, self.other_brand, self.category, self.price, self.styles, self.description, self.features, self.picURL, self.URL]


class brand():
    '''A bass brand

    Instance Attributes
    -------------------
    brand_name: string 
        The name of the brand

    brand_country: string 
        The country where the brand headquaters in

    brand_description: string
        A short description about the brand

    URL: string
        A link to the official website of the brand. If not available, a link to the Wikipedia page of the brand
    '''

    def __init__(self, brand_name, brand_country, brand_description, URL):
        self.brand_name = brand_name
        self.brand_country = brand_country
        self.brand_description = brand_description
        self.URL = URL

    def info(self):
        '''Report a list of information of a brand

        Parameters
        ----------
        None

        Returns
        ----------
        A list of basic information of a brand
        '''
        return [self.brand_name, self.brand_country, self.brand_description, self.URL]


# Functions in this part work on the caching
def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into the CACHE_DICT dictionary.
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

# Functions in this part work on web scrapping 
def make_request(url):
    '''Make a request to the Web using the url
    
    Parameters
    ----------
    url: string
        The URL for the API/scrapping endpoint
    
    Returns
    -------
    dict
        the data returned from making the request in the form of a dictionary
    '''
    if "https://www.googleapis.com/youtube/v3/search" in url:
        response = requests.get(url).json()
    else:
        response = requests.get(url).text
    return response


def make_request_with_cache(url):
    '''Check the cache for a saved result for this url. If the result is found, return it. Otherwise send a new request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    
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
    '''Get the name and the URL of all basses from Guitar Center online shop
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary having names of the basss as keys, and url of the product page as values
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
    '''Make an instances from a Guitar Center product page.
    
    Parameters
    ----------
    site_url: string
        The URL for a product page in Guitar Center
    
    Returns
    -------
    instance
        a bass instance
    '''
    response = make_request_with_cache(site_url)
    soup = BeautifulSoup(response, 'html.parser')
    if soup.find('div', class_='titleWrap') is None:
        pass
    else:
        product_name = soup.find('div', class_='titleWrap').text.lstrip()
        brandname = soup.find('div', class_='titleWrap').find('span', class_='brand').text
        brand_and_other = change_brandname_into_number(brandname)
        brand = brand_and_other[0]
        other_brand = brand_and_other[1]
        picURL = soup.find('div', class_='product-left').find('img')['src']
        try:
            price = float(soup.find('span', class_='topAlignedPrice').text.strip().strip('$').replace(',', ''))
        except:
            price = None

        try:
            description = soup.find('section', id='product-overview').find('p', class_='description').text
        except:
            description = None
        
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
            features = None
        return bass(product_name, brand, other_brand, category, price, styles, description, features, picURL, site_url)


def change_brandname_into_number(brandname):
    '''Change the brand name into id.
    
    Parameters
    ----------
    brandname: string
        The name of the brand
    
    Returns
    -------
    int or string
        The id of the brand, return the original brandname if the id is not available
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    read_brand_db='''
    SELECT BrandId, BrandName
    FROM brands
    '''
    brandlist = cur.execute(read_brand_db)
    for brand in brandlist:
        if brand[1].lower() in brandname.lower():
            brandcode = brand[0]
    conn.close()
    try:
        return (int(brandcode), None)
    except:
        return (0, brandname)


def get_youtube_video_url(bassname):
    '''Get the youtube video URL for the bass
    
    Parameters
    ----------
    bassname: string
        The name of the bass
    
    Returns
    -------
    string or None
        URL of the youtube page. return None if there is no result.
    '''
    base_url = "https://www.googleapis.com/youtube/v3/search?"
    bassname = "%20".join(bassname.split(" "))
    query = str(base_url + "part=snippet&maxResults=1&q=" + bassname + "&key=" + API_KEY)
    response = make_request_with_cache(query)
    print(response)
    try:
        finalreturns = str(response['items'][0]['id']['videoId'])
    except: finalreturns = None
    return finalreturns


def get_brands():
    '''Get the name and the URL of all brands from Wikipedia "List of Guitar Manufacturers" page.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary having names of the brands as keys, and url of the Wikipedia page as values
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
    '''Make an instances from a Wikipedia page.
    
    Parameters
    ----------
    site_url: string
        The URL for a product page in WikiPedia
    
    Returns
    -------
    instance
        a brand instance
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
            if country is not None:
                country = country.strip(',').strip('.').strip()
        elif 'country' in info_dict.keys():
            country = info_dict['country'].text
            if country is not None:
                country = country.strip(',').strip('.').strip()
        if 'website' in info_dict.keys():
            website = info_dict['website'].a['href']
        else:
            website = site_url
    except:
        website = site_url
        country = None

    row_description = soup.find('div', id='mw-content-text').find('div', class_='mw-parser-output').find_all('p')
    if 'coordinates' in str(row_description[0]):
        description = row_description[1].text
    else:
        description = row_description[0].text
    
    return brand(brandname, country, description, website)


# Functions in this part work with the database
def create_db():
    '''Create the databases for basses and brands

    Parameters
    ----------
    None

    Returns
    ----------
    None
    '''

    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    drop_basses = 'DROP TABLE IF EXISTS "Basses"'
    drop_brands = 'DROP TABLE IF EXISTS "Brands"'
    create_basses = '''
        CREATE TABLE IF NOT EXISTS "Basses" (
            'BassId' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'ModelName' TEXT NOT NULL,
            'Brand' INTEGER NOT NULL,
            'OtherBrand' TEXT,
            'Category' INTEGER NOT NULL,
            'Price' DECIMAL,
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


def save_to_basses(bass):
    '''Save the bass to database.
    
    Parameters
    ----------
    bass: instance
        A bass instance contains all the data to be stored
    
    Returns
    -------
    None
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    insert_basses = '''
    INSERT INTO Basses
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    cur.execute(insert_basses, bass)
    conn.commit()


def save_to_brands(brand):
    '''Save the brand to database.
    
    Parameters
    ----------
    brand: instance
        A brand instance contains all the data to be stored
    
    Returns
    -------
    None
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    insert_brands = '''
    INSERT INTO Brands
    VALUES (NULL, ?, ?, ?, ?)
    '''
    cur.execute(insert_brands, brand)
    conn.commit()    

# Functions in this part are for generating the inerface
@app.route('/')
def index():
    '''Generate the mainpage of my applicaiton.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    webpage
        the mainpage.
    '''
    return render_template('index.html')


@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    '''Generate the results page when the search is sent.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    webpage
        the results page.
    '''
    try:
        keywords = request.form["keyword"]
    except:
        keywords = None
    basstype = request.form["basstype"]
    try:
        lowestprice = request.form["lowestprice"]
    except:
        lowestprice = None
    try:
        highestprice = request.form["highestprice"]
    except:
        highestprice = None
    try:
        strings = request.form["strings"]
    except:
        strings = None
    allbasses = return_results(keywords, basstype, lowestprice, highestprice, strings)
    return render_template('results.html', 
    keywords = keywords,
    basstype = basstype,
    strings = strings,
    len = len(allbasses),
    Basses = allbasses
    )


@app.route('/seevideo', methods=['POST'])
def video_page():
    '''Generate the video page.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    webpage
        the video page.
    '''
    bassname = request.form["bassname"]
    bassdata = find_a_bass(bassname)
    youtubelink = get_youtube_video_url(bassname)
    return render_template('seevideo.html',
    bassname = bassname,
    youtubelink = youtubelink,
    bassdata = bassdata)


@app.route('/brands')
def brands():
    '''Generate the brands page.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    webpage
        the brands page.
    '''
    allbrands = return_brands()
    return render_template('Allbrands.html', 
    len = len(allbrands),
    Brands = allbrands
    )


@app.route('/brandanalysis')
def brandanalysis():
    '''Generate the brands analysis page.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    webpage
        the brands analysis page.
    '''
    brands_country_dict = brands_country_analysis()
    countries = []
    counts = []
    for key,value in brands_country_dict.items():
        countries.append(key)
        counts.append(value)
    data = [go.Pie(labels=countries, values=counts, hole=.3)]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    bass_brands_dict = bass_by_brands()
    brands = []
    brandscounts = []
    for key,value in bass_brands_dict.items():
        brands.append(key)
        brandscounts.append(value)
    data2 = [go.Bar(x=brands, y=brandscounts)]
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)

    bass_price_dict = bass_by_price()
    basses = []
    prices = []
    brandsfortag = []
    for key,value in bass_price_dict.items():
        basses.append(key)
        prices.append(value[1])
        brandsfortag.append(value[0])
    data3 = [go.Scatter(x=basses, y=prices, mode='markers', hovertext=basses)]
    graphJSON3 = json.dumps(data3, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('brandanalysis.html', plot=graphJSON, plot2=graphJSON2, plot3=graphJSON3)

# Functions below are for analyzing purpose
def generate_query(keywords, basstype, lowestprice, highestprice, strings):
    '''Generate a query to search with the basses table.
    
    Parameters
    ----------
    keywords: string
        A keyword used to do a cross field search

    basstype: string
        The type of the bass

    lowestprice: string
        The lowest price of the basses that users would like to search for

    highestprice: string
        The highest price of the basses that users would like to search for
    
    strings: string
        The number of the bass string
    
    Returns
    -------
    string
        A SQL query used to search with basses table
    '''
    query_bass = '''
    SELECT ModelName, IFNULL(Brands.BrandName, OtherBrand), Price, Styles, Description, Features, PicURL, Basses.URL, Brands.BrandCountry
    FROM Basses
    LEFT OUTER JOIN Brands 
	ON Basses.Brand = Brands.BrandId
    '''
    querylist = []
    if len(keywords)>0:
        keywordquery = '(ModelName LIKE "%' + keywords + '%" OR Brands.BrandName LIKE "%' + keywords + '%" OR OtherBrand LIKE "%' + keywords + '%" OR Styles LIKE "%' + keywords + '%" OR Description LIKE "%' + keywords + '%" OR Features LIKE "%' + keywords + '%")'
        querylist.append(keywordquery)
    if len(basstype)>0:
        querylist.append('Category LIKE "%' + basstype + '%"')
    if len(lowestprice)>0:
        querylist.append('Price >=' + str(lowestprice))
    if len(highestprice)>0:
        querylist.append('Price <=' + str(highestprice))
    if strings is not None:
        if len(strings)>0:
            querylist.append('Category LIKE "%' + strings + '%"')
    
    if len(querylist)>0:
        i = 0
        for query in querylist:
            if i == 0:
                query_bass = query_bass + " WHERE " + query
                i += 1
            else:
                query_bass = query_bass + " AND " + query
    return query_bass


def return_results(keywords, basstype, lowestprice, highestprice, strings):
    '''Get the basses that meet the provided criteria
    
    Parameters
    ----------
    keywords: string
        A keyword used to do a cross field search

    basstype: string
        The type of the bass

    lowestprice: string
        The lowest price of the basses that users would like to search for

    highestprice: string
        The highest price of the basses that users would like to search for
    
    strings: string
        The number of the bass string
    
    Returns
    -------
    list
        A list of basses that meet the provided criteria
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    query = generate_query(keywords, basstype, lowestprice, highestprice, strings)
    results = cur.execute(query)
    conn.commit()
    result_list=[]
    for basses in results:
        result_list.append(basses)
    return result_list


def find_a_bass(bassname):
    '''Get a bass with it's name
    
    Parameters
    ----------
    bassname: string
        Name of the bass
    
    Returns
    -------
    list
        A list of data for the bass
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    querybase = '''
    SELECT ModelName, IFNULL(Brands.BrandName, OtherBrand), Price, Styles, Description, Features, PicURL, Basses.URL
    FROM Basses
    LEFT OUTER JOIN Brands 
	ON Basses.Brand = Brands.BrandId
    '''
    query = querybase + 'WHERE ModelName = "' + bassname + '"'
    results = cur.execute(query)
    conn.commit()
    result= list(results)[0]
    return result


def return_brands():
    '''Get all of the brands in brands table
    
    Parameters
    ----------
    None
    
    Returns
    -------
    list
        A list of brands
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    query = '''
    SELECT BrandName, BrandCountry, BrandDescription, URL
    FROM Brands
    '''
    results = cur.execute(query)
    conn.commit()
    result_list=[]
    for brands in results:
        result_list.append(brands)
    return result_list


def return_brand_countries():
    '''Get all of the countries the brands bassed
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary with the countries as keys, and all values is None
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    query = '''
    SELECT DISTINCT Brands.BrandCountry
    FROM Brands
    '''
    results = cur.execute(query)
    conn.commit()
    result_list=[]
    for country in results:
        result_list.append(country[0])
    return dict.fromkeys(result_list)


def return_bass_brands():
    '''Get all of the brands who have their basses selling in Guitar Center
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary with the brands as keys, and all values is None
    '''
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    query = '''
    SELECT DISTINCT IFNULL(Brands.BrandName, OtherBrand)
    FROM Basses
    LEFT OUTER JOIN Brands 
        ON Basses.Brand = Brands.BrandId
    '''
    results = cur.execute(query)
    conn.commit()
    result_list=[]
    for brand in results:
        result_list.append(brand[0])
    return dict.fromkeys(result_list)


def brands_country_analysis():
    '''Analyze through how many bass brands are in each countries
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary with countries as keys, and the number of the brands headquartered in the country as values
    '''
    allbrands = return_brands()
    US_list = ["United States of America", "US", "USA", "American"]
    UK_list = ["England", "UK"]
    country_dict = return_brand_countries()

    for brand in allbrands:
        if brand[1] in country_dict.keys():
            if country_dict[brand[1]] is None:
                country_dict[brand[1]] = 0
            else:
                country_dict[brand[1]] = country_dict[brand[1]] + 1
    combinelist = []
    for key,value in country_dict.items():
        if key in US_list:
            country_dict["United States"] += value
            combinelist.append(key)
        if key in UK_list:
            country_dict["United Kingdom"] += value
            combinelist.append(key)
        if key is None:
            country_dict[""] += value
            combinelist.append(key)
    for combined in combinelist:
        del country_dict[combined]
    country_dict["N/A"] = country_dict[""]
    del country_dict[""]
    blanklist = []
    for key,value in country_dict.items():
        if value == 0:
            blanklist.append(key)
    for blank in blanklist:
        del country_dict[blank]
    return country_dict


def bass_by_brands():
    '''Analyze through how many bass in the online store are made by each brands
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary with brands as keys, and the number of the basses in the online store as values. Sorted by the number of the basses
    '''
    allbasses = return_results("", "", "", "", "")
    brand_dict = return_bass_brands()
    for bass in allbasses:
        if bass[1] in brand_dict.keys():
            if brand_dict[bass[1]] is None:
                brand_dict[bass[1]] = 0
            else:
                brand_dict[bass[1]] = brand_dict[bass[1]] + 1
    blanklist = []
    for key,value in brand_dict.items():
        if value <= 5:
            blanklist.append(key)
    for blank in blanklist:
        del brand_dict[blank]
    brand_dict = sorted(brand_dict.items(), key=lambda kv: kv[1], reverse=True)
    brand_dict = collections.OrderedDict(brand_dict)
    return brand_dict


def bass_by_price():
    '''List out all the basses with its brand and price, and sorted with the price.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        A dictionary with basses as keys, and a list of brand and price as values
    '''
    allbasses = return_results("", "", "1", "", "")
    bass_dict = {}
    for bass in allbasses:
        bass_dict[bass[0]] = [bass[1], bass[2]]
    bass_dict = sorted(bass_dict.items(), key=lambda kv: kv[1][1])
    bass_dict = collections.OrderedDict(bass_dict)
    return bass_dict


if __name__ == "__main__":
# UNCOMMENT THE PART BELOW TO GET THE UPDATED BASS AND BRAND INFORMATION
    # create_db()
    # CACHE_DICT = open_cache()
    # bass_url_dict = get_basses()
    # brand_url_dict = get_brands()
    # for keys,values in brand_url_dict.items():
    #     save_to_brands(get_brands_instance(keys, values).info())
    # for keys,values in bass_url_dict.items():
    #     try:
    #         save_to_basses(get_bass_instance(values).info())
    #     except:
    #         pass
    app.run(debug=True)

