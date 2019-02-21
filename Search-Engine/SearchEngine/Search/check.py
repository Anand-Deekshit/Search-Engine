#from Search.main import *
import pymysql as MySQLdb
from .spider import Spider


class Check:
    word = ""
    urlsDict = []
    def __init__(self,word):
        Check.word = word
        Check.urlsDict = Check.get_urls_dict()
    

    @staticmethod
    def sortUrls(priorityDict):
        sortedUrls = []
        print("PRIORITYDICT : ", priorityDict)
        sortedPairs = sorted(priorityDict.items(), key=lambda kv: kv[1])
        print("SORTED PAIRS : ", sortedPairs)
        for pair in sortedPairs:
            #print(pair[0])
            sortedUrls.append(pair[0])
        print(sortedUrls)
        sortedUrls.reverse()
        print(sortedUrls)
        return sortedUrls


    @staticmethod
    def get_urls_dict():
        priorityDict = {}
        connection = MySQLdb.connect("localhost", "root", "root", "keywordurldb", autocommit=True)
        cursor = connection.cursor()
        query = "SELECT urls, (title + meta_description + meta_keyword + in_url + (weight * 10)) FROM keywordurlpair WHERE keyword=%s"
        var = Check.word
        cursor.execute(query, (var,))
        urlsData = cursor.fetchall()
        for tup in urlsData:
            priorityDict[tup[0]] = float(tup[1])
        category = Spider.get_category(Check.word)
        query = "SELECT urls FROM keywordurlpair WHERE category=%s"
        var = int(category)
        cursor.execute(query, (var,))
        category_urls = cursor.fetchall()
        #for tup in range(len(urlsData)):
            #urlList.append(urlsData[tup][0])
        for tup in range(len(category_urls)):  
            if category_urls[tup][0] not in list(priorityDict.keys()):
                weight = Spider.get_count(Check.word, category_urls[tup][0])
                in_url = 0
                if weight > 0.1:
                    if Check.word in category_urls[tup][0]:
                        in_url = 8
                    priorityDict[category_urls[tup][0]] = float((weight * 10) + in_url)
                    #urlList.append(category_urls[tup][0])
        connection.close()
        #sortedUrls = Check.sortUrls(priorityDict)
        return priorityDict


        @staticmethod
        def sortUrls(priorityDict):
            sortedUrls = []
            sortedPairs = sorted(priorityDict.items(), key=lambda kv: kv[1])
            for pair in sortedPairs:
                sortedUrls.append(pair[0])
            sortedUrls = sortedUrls.reverse()
            print(sortedUrls)
            return sortedUrls
            