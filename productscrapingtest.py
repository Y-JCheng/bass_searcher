from bs4 import BeautifulSoup
import requests
import json
import sqlite3
import collections

def generate_query(keywords, basstype, lowestprice, highestprice, strings):
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
    conn = sqlite3.connect('bassdb.sqlite')
    cur = conn.cursor()
    query = generate_query(keywords, basstype, lowestprice, highestprice, strings)
    results = cur.execute(query)
    conn.commit()
    result_list=[]
    for basses in results:
        result_list.append(basses)
    return result_list


def bass_by_price():
    allbasses = return_results("", "", "1", "", "")
    bass_dict = {}
    for bass in allbasses:
        bass_dict[bass[0]] = [bass[1], bass[2]]
    bass_dict = sorted(bass_dict.items(), key=lambda kv: kv[1][1])
    bass_dict = collections.OrderedDict(bass_dict)
    print(bass_dict)

bass_by_price()