#! /usr/bin/env python
#! coding=utf-8
#! author kbdancer @nocrap.org
#! python btsearch.py adult-video 50

import threading
import requests
import Queue
import sys
import re

def bThread(urllist):
    
    threadl = []
    queue = Queue.Queue()
    for url in urllist:
        queue.put(url)

    for x in xrange(0, int(sys.argv[2])):
        threadl.append(tThread(queue))
        
    for t in threadl:
        t.start()
    for t in threadl:
        t.join()        

class tThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        
        while not self.queue.empty(): 
            url = self.queue.get()
            try:
                decodeSomething(url)
            except:
                continue

def getContent():

	url = "http://www.btmayi.me/search/"+ sys.argv[1] +"-first-asc-1"

	try:
		req = requests.get(url=url,verify = False,timeout = 20)
		responseStr = req.content
		
		temppage = re.findall(r'<div class="bottom-pager">(.+?)</div>',responseStr,re.S)[0].replace('\n','')
		pagestr = re.findall(r'<a href="(.+?)">',temppage)

		if len(pagestr) < 1:
			# test if only one page
			pagespan = re.findall(r'<span>(.+?)"</span>',temppage)
			if len(pagespan) < 1:
				print 'Can not find any page ! Exit!'
				sys.exit()
			else:
				maxpage = 1
		else:
			maxpage = int(re.findall(r'<a href="(.+?)">',temppage)[-1].split('asc-')[1])

		urllist = []
		
		for pl in range(1,maxpage+1):
			urllist.append("http://www.btmayi.me/search/"+ sys.argv[1] +"-first-asc-"+str(pl))

		print "The keyword is "+ sys.argv[1] +", Page count is "+str(len(urllist)) +", Thread is "+sys.argv[2]+"!"

		ifstart = raw_input("Start ?(Y/N)")
		if ifstart.lower() == "y":
			bThread(urllist)
		else:
			print 'Cancel!'

	except Exception,e:
		print e
		pass

def decodeSomething(url):
	try:
		tmpreq = requests.get(url=url,verify = False,timeout = 20)
		htmlstr = tmpreq.content

		magnet = re.findall(r'href="magnet(.+?)"',htmlstr)
		thunder = re.findall(r'href="thunder(.+?)"',htmlstr)
		title = re.findall(r'<div class="item-list">(.+?)</div>',htmlstr,re.S)

		for x in range(0,len(magnet)):
			tempTtitle = title[x].replace('<span class="highlight">','').replace('</span>','').replace('\n',' ')
			size = re.findall(r'<span>(.+?)</p>',tempTtitle)
			titleText = re.findall(r'<p>(.+?)<span>',tempTtitle)
		
			# to fix some ad script 
			trashcode = re.findall(r'<a(.+?)script>',titleText[0])

			if len(trashcode) > 0:
				trashTitle = titleText[0]
				for t in range(0,len(trashcode)):
					trashTitle = trashTitle.replace('<a'+trashcode[t]+'script>',"")
				realTitle = trashTitle
			else:
				realTitle = titleText[0]

			print "-"*110 +"\nTitle: "+ realTitle +"\nMagnet: magnet"+ magnet[x] +"\nThunder: thunder"+ thunder[x] +"\nSize: "+size[0]
	except Exception,e:
		print e
		pass

if __name__ == '__main__':
	try:
		getContent()
	except KeyboardInterrupt:
		print '\nCancel.'
