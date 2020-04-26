from bs4 import BeautifulSoup
import requests
import json
import sqlite3

def return_brand_countries():
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


def brands_country_analysis():
    allbrands = return_brands()
    US_list = ["United States of America", "US", "USA", "American"]
    UK_list = ["England", "UK"]
    country_dict = return_brand_countries()

    for brand in allbrands:
        print(brand)
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
    print(country_dict)
    for combined in combinelist:
        del country_dict[combined]
    country_dict["N/A"] = country_dict[""]
    del country_dict[""]
    print(country_dict)


def return_brands():
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


if __name__ == "__main__":
    brands_country_analysis()