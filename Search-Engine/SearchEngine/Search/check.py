#from Search.main import *
import pymysql as MySQLdb
from .spider import Spider

class Check:
    word = ""
    wordUrls = []
    def __init__(self,word):
        Check.word = word
        Check.wordUrls = Check.get_urls()
        

    @staticmethod
    def get_urls():
        urlList = []
        connection = MySQLdb.connect("localhost", "root", "root", "keywordurldb", autocommit=True)
        cursor = connection.cursor()
        query = "SELECT urls FROM keywordurlpair WHERE keyword=%s"
        var = Check.word
        cursor.execute(query, (var,))
        urlsData = cursor.fetchall()
        query = "SELECT urls FROM keywordurlpair WHERE "
        category = Spider.get_category(Check.word)
        query = "SELECT urls FROM keywordurlpair WHERE category=%s"
        var = int(category)
        cursor.execute(query, (var,))
        category_urls = cursor.fetchall()
        for tup in range(len(urlsData)):
            urlList.append(urlsData[tup][0])
        for tup in range(len(category_urls)):
            if category_urls[tup][0] not in urlList:
                weight = Spider.get_count(Check.word, category_urls[tup][0])
                if weight > 0.08:
                    urlList.append(category_urls[tup][0])
        connection.close()
        return list(set(urlList))

        
