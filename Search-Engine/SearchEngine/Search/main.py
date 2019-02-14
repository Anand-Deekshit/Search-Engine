# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:23:27 2019

"""

import threading
from queue import Queue
from spider import Spider

queue = Queue()
SEED = "http://dmoz-odp.org"
queue.put(SEED)
NUMBER_OF_THREADS = 8
Spider(SEED)
maxPages = 5
maxDepth = 3
depth = 0

#Create worker threads
def create_workers():
    print("Workers")
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()
        
#Do the next job in the queue
def work():
    while True:
        print("Work")
        url = queue.get(timeout=30)
        Spider.crawl_page(threading.current_thread().name, url, maxPages, maxDepth, depth)
        queue.task_done()
        
#Each queue link is a new job
def create_jobs():
    for link in Spider.toCrawl:
        queue.put(link)
    queue.join()
    crawl()
    
#Check if there are links in queue
def crawl():
    if len(Spider.toCrawl) > 0:
        print("ToCrawl length:", len(Spider.toCrawl))
        create_jobs()
    else:
        print(len(Spider.toCrawl))
        print("Phuss")
        
create_workers()
crawl()