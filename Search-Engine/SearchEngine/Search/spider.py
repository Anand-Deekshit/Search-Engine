# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:56:57 2019

@author: Anand
"""

from sklearn.datasets import fetch_20newsgroups
#Because of polynomial distribution(Study)
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
#To vectorize the strings into vectors(study)
from sklearn.feature_extraction.text import TfidfVectorizer
#To map the vecotorizer with the model parellally(study)
from sklearn.pipeline import make_pipeline
from bs4 import BeautifulSoup
import sys
import requests
from operator import is_not
from functools import partial
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import MySQLdb
data = fetch_20newsgroups()
categories = data.target_names
train = fetch_20newsgroups(subset='train', categories=categories)
test = fetch_20newsgroups(subset='test', categories=categories)
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(train.data, train.target)

class Spider:
    
    SEED = ""
    toCrawl = []
    crawled = []
    pagesVisited = 0
    
    def __init__(self, SEED):
        print("In spider")
        Spider.SEED = SEED
        Spider.crawled = Spider.urlscrawled_to_list()
        Spider.toCrawl = Spider.get_links_from_db()
        if len(Spider.toCrawl) == 0:
            Spider.toCrawl.append(Spider.SEED)
        #print(Spider.crawled)
    
    def urlscrawled_to_list():
        connection = MySQLdb.connect("localhost", "root", "root", "crawled", autocommit=True)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM crawledurls")
        crawledUrls = cursor.fetchall()
        #connection.commit()
        connection.close()
        crawledList = []
        for urlTuple in crawledUrls:
            crawledList.append(urlTuple[0])
        return crawledList
    
    def get_links_from_db():
        connection = MySQLdb.connect("localhost", "root", "root", "tocrawl", autocommit=True)
        cursor = connection.cursor()
        query = """SELECT * FROM linkstocrawl"""
        cursor.execute(query)
        toCrawlTuple = cursor.fetchall()
        #connection.commit()
        connection.close()
        toCrawl = Spider.to_crawl_list(toCrawlTuple)
        return toCrawl
    
    @staticmethod
    def to_crawl_list(toCrawlTuple):
       toCrawl = []
       for link in toCrawlTuple:
           toCrawl.append(link[0])
       return toCrawl
   
    @staticmethod
    def clear_to_crawl_db():
        connection = MySQLdb.connect("localhost", "root", "root", "tocrawl", autocommit=True)
        cursor = connection.cursor()
        cursor.execute("TRUNCATE linkstocrawl")
        connection.close()
    
    @staticmethod
    def write_to_toCrawl_db():
        Spider.clear_to_crawl_db()
        connection = MySQLdb.connect("localhost", "root", "root", "tocrawl", autocommit=True)
        cursor = connection.cursor()
        print("HERE")
        variable = []
        for link in Spider.toCrawl:
            if link != 'None' and link[0] != '.':
                variable.append((link,))
        try:
            query = """INSERT INTO linkstocrawl(link) VALUES(%s)"""
            print("--------")
            cursor.executemany(query, variable)
            print("HERE2")
        except:
            pass
        connection.close()
        
    @staticmethod
    def remove_from_tocrawl_db(url):
        connection = MySQLdb.connect("localhost", "root", "root", "tocrawl", autocommit=True)
        cursor = connection.cursor()
        print("Length Before: ", cursor.execute("SELECT * FROM linkstocrawl"))
        query = """DELETE FROM linkstocrawl WHERE link=%s"""
        variable = url
        cursor.execute(query, (variable,))
        print("DELETED")
        print("Length After: ", cursor.execute("SELECT * FROM linkstocrawl"))
        #connection.commit()
        print("COMMITED")
        connection.close()
        
    @staticmethod
    def remove_crawled_from_tocrawl():
        Spider.toCrawl = list(set(Spider.toCrawl) - set(Spider.crawled))
    
    @staticmethod
    def crawl_page(threadName, url, maxPages, maxDepth, depth):
        print("In crawl page")
        print("To Crawl: ", len(Spider.toCrawl))
        links = Spider.get_links(url)
        Spider.toCrawl = Spider.toCrawl + links
        if Spider.pagesVisited < maxPages:
            if url not in Spider.crawled:
                data = Spider.get_data(url)
                if url in Spider.toCrawl:
                    #Spider.remove_from_tocrawl_db(url)
                    #removing all occurences of the url in tocrawl
                    print("Length before: ", len(Spider.toCrawl))
                    Spider.toCrawl = list(set(Spider.toCrawl) - set(Spider.crawled))
                    Spider.toCrawl.remove(url)
                    print("Length after: ", len(Spider.toCrawl))
                Spider.add_to_keywords_db(data, url)
                Spider.crawled.append(url)
                print("Crawled: ", Spider.crawled)
                Spider.add_to_crawled_db(url)
                Spider.write_to_toCrawl_db()
                Spider.pagesVisited = Spider.pagesVisited + 1
                print("Pages Visited: ", Spider.pagesVisited)
        else:
            print("Exiting")
            sys.exit()
            
    @staticmethod
    def get_links(url):
        print("In get links from page")
        urls = []
        htmlData = requests.get(url + "/")
        htmlString = htmlData.text
        dataObject = BeautifulSoup(htmlString, features="html.parser")
        for link in dataObject.find_all("a"):
            href = str(link.get('href'))
            if href != "None" and len(href) != 0 and href[0] != '.' and href != 'None/':
                #print(href, " : ", len(href))
                if href[0] == '/' and href[len(href) - 1] == '/':
                    urls.append(Spider.SEED + href[:len(href) - 1])
                elif href[0] == '/' and href[len(href) - 1] != '/':
                    urls.append(Spider.SEED + href)
                else:
                    if href[len(href) - 1] == '/':
                        urls.append(href[:len(href) - 1])
            else:
                urls.append(href)
                
        urls = list(filter(partial(is_not, None), urls))
        return urls
    
    @staticmethod
    def get_data(url):
        print("In get data")
        data = ""
        htmlData = requests.get(url + "/")
        htmlString = htmlData.text
        dataObject = BeautifulSoup(htmlString, features="html.parser")
        titleData = dataObject.title.string
        data = data + titleData
        description = ""
        for meta in dataObject.find_all("meta"):
            if str(meta.get("name")) == "description":
                description = meta.get("content")
        data = data + " " + description
        metaKeyword = ""
        for meta in dataObject.find_all("meta"):
            if str(meta.get("name")) == "keywords":
                metaKeyword = meta.get("content")
        data = data + " " + metaKeyword
        data = Spider.remove_special_characters(data)
        data = Spider.remove_stopwords(data)
        return data
                
    @staticmethod
    def remove_special_characters(data):
        newData = re.sub(r"[^a-zA-Z0-9]+"," ",data)
        newData = newData.lower()
        return newData
    
    @staticmethod
    def remove_stopwords(data):
        stopWords = set(stopwords.words('english'))
        stopWords.add("\n")
        stopWords.add("\t")
        wordsFromData = word_tokenize(data)
        dataWithoutStopWords = []
        for word in wordsFromData:
            if not word in stopWords:
                dataWithoutStopWords.append(word)
        return dataWithoutStopWords
    
    @staticmethod
    def get_category(word):
        return model.predict([word])[0]
    
    @staticmethod
    def get_count(word, url):
        htmlData = requests.get(url + "/")
        htmlString = htmlData.text
        data = Spider.remove_special_characters(htmlString)
        dataList = data.split(" ")
        dataLength = len(dataList)
        count = data.count(word)
        weight = float(count / dataLength) * 100
        return float(weight)
    
    
    @staticmethod
    def add_to_keywords_db(data, url):
        print("In add words")
        print(data)
        connection = MySQLdb.connect("localhost", "root", "root", "keywordurldb", autocommit=True)
        cursor = connection.cursor()
        query = """SELECT keyword FROM keywordurlpair"""
        cursor.execute(query)
        keywordsInDB = cursor.fetchall()
        list_of_keywordsInDB = Spider.keywordstuple_to_list(keywordsInDB)
        htmlData = requests.get(url + "/")
        htmlString = htmlData.text
        dataObject = BeautifulSoup(htmlString, features="html.parser")
        #print(keywordsInDB)
        for word in data:
            if word in list_of_keywordsInDB:
                query = """SELECT urls FROM keywordurlpair WHERE keyword=%s"""
                variable = [str(word)]
                cursor.execute(query, variable)
                urlsForWord = cursor.fetchall()
                list_of_urlsForWord = Spider.urlstuple_to_list(urlsForWord)
                if not url in list_of_urlsForWord:
                    list_of_urlsForWord.append(url)
                    title = Spider.check_in_title(word, dataObject)
                    description = Spider.check_in_description(word, dataObject)
                    metaKeyword = Spider.check_in_keyword(word, dataObject)
                    category = Spider.get_category(word)
                    weight = Spider.get_count(word, url)
                    inUrl = 0
                    if word in url:
                        inUrl = 8
                    #cursor.execute("update keywordurlpair set urls =? where keyword=?",(list_of_urlsForWord, word))
                    try:
                        query = """INSERT INTO keywordurlpair(keyword, urls, title, meta_description, meta_keyword, category, weight, in_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                        variable = [str(word), str(url), int(title), int(description), int(metaKeyword), int(category), float(weight), int(inUrl)]
                        cursor.execute(query, variable)
                        print("DONE")
                        #connection.commit()
                    except:
                        pass  
            else:
                title = Spider.check_in_title(word ,dataObject)
                description =Spider.check_in_description(word, dataObject)
                metaKeyword = Spider.check_in_keyword(word, dataObject)
                category = Spider.get_category(word)
                weight = Spider.get_count(word, url)
                inUrl = 0
                if word in url:
                    inUrl = 8
                try:
                    query = """INSERT INTO keywordurlpair(keyword, urls, title, meta_description, meta_keyword, category, weight, in_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                    variable = [str(word), str(url), int(title), int(description), int(metaKeyword), int(category), float(weight), int(inUrl)]
                    cursor.execute(query, variable)
                    print("DONE")
                    #connection.commit()
                except:
                    pass
        connection.close()
        
    @staticmethod
    def add_to_crawled_db(url):
        print("In add to crawled")
        connection = MySQLdb.connect("localhost", "root", "root", "crawled")
        cursor = connection.cursor()
        try:
            query = """INSERT INTO crawledurls VALUES(%s)"""
            variable = [str(url)]
            cursor.execute(query, variable)
            print("--HERE1--")
            connection.commit()
            #Spider.remove_from_tocrawl_db(url)
            #Spider.toCrawl.remove(url)
        except:
            pass
        connection.close()
        
    @staticmethod            
    def check_in_title(word, dataObject):
    #print("WORD : ", word)
        title = dataObject.title.string
        if word in title.lower():
            return 4
        return 0
    
    @staticmethod
    def check_in_description(word, dataObject):
        description = ""
        for meta in dataObject.find_all("meta"):
            if str(meta.get("name")) == "description":
                description = meta.get("content")
        if word in description.lower():
            return 1
        return 0
    
    @staticmethod
    def check_in_keyword(word, dataObject):
        metaKeyword = ""
        for meta in dataObject.find_all("meta"):
            if str(meta.get("name")) == "keywords":
                metaKeyword = meta.get("content")
        if word in metaKeyword.lower():
            return 2
        return 0
    
    @staticmethod
    #list of keywords in db
    def keywordstuple_to_list(keywordsInDB):
        converting_to_keywordlist = []
        for each_tuple in keywordsInDB:
            converting_to_keywordlist.append(each_tuple[0])
        return converting_to_keywordlist
    
    @staticmethod
    #list of urls for words in db
    def urlstuple_to_list(urlsForWord):
        converting_to_urllist = []
        for each_tuple in urlsForWord:
            converting_to_urllist.append(each_tuple[0])
        return converting_to_urllist
    
