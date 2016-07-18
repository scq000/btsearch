#! /usr/bin/env python
#! coding=utf-8
#! author kbdancer @92ez.com

import threading
import requests
import Queue
import math
import json
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

def bThread(urllist):
	
	threadl = []
	queue = Queue.Queue()
	for url in urllist:
		queue.put(url)

	for x in xrange(0, 20):
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
				decodeHTML(url)
			except:
				continue

def getUrlByBTmayi():
	keyword = sys.argv[1]
	url = "http://www.btany.com/search/"+ keyword +"-first-asc-1"
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	try:
		req = requests.get(url=url,verify = False,headers = headers,timeout = 20)
		responseStr = req.content

		# no result
		if len(responseStr.split('<span>无<b>')) > 1:
			return json.dumps({"code":-1,"msg":"can not find any page!"})
			sys.exit()

		temppage = re.findall(r'<div class="bottom-pager">(.+?)</div>',responseStr,re.S)[0].replace('\n','')
		pagestr = re.findall(r'<a href="(.+?)">',temppage)

		if len(pagestr) < 1:
			# only one page
			maxpage = 1
		else:
			maxpage = int(re.findall(r'<a href="(.+?)">',temppage)[-1].split('asc-')[1])

		urllist = []

		for pl in range(1,maxpage+1):
			tmpurl = {"site":"btany.com","url":"http://www.btany.com/search/"+ keyword +"-first-asc-"+str(pl)}
			urllist.append(tmpurl)

		bThread(urllist)

	except Exception,e:
		print e

def getUrlByBTwalk():
	keyword = sys.argv[1]
	url = "http://www.btwalk.org/search/"+ keyword +"/1-1.html"
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	try:
		req = requests.get(url = url,verify = False,headers = headers,timeout = 20)
		responseStr = req.content.replace('\r\n','')

		totalCount = int(re.findall(r'<span>大约 (.+?) 条结果',responseStr)[0])
		totalPage = int(math.ceil(float(totalCount)/10))

		urllist = []
		for pl in range(1,totalPage + 1):
			tmpurl = {"site":"btwalk.org","url":"http://www.btwalk.org/search/"+ keyword +"/"+ str(pl) +"-1.html"}
			urllist.append(tmpurl)

		bThread(urllist)

	except Exception,e:
		print e

def getUrlBy97ki():
	keyword = sys.argv[1]
	url = "http://www.97ki.com/"+ keyword +"-first-asc-1"
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	try:
		req = requests.get(url = url,verify = False,headers = headers,timeout = 20)
		responseStr = req.content.replace('\n','')

		totalPage = int(re.findall(r'first-asc-(.+?)">',responseStr)[-1])

		urllist = []
		for pl in range(1,totalPage + 1):
			tmpurl = {"site":"97ki.com","url":"http://www.97ki.com/"+ keyword +"-first-asc-"+str(pl)}
			urllist.append(tmpurl)

		print urllist
		bThread(urllist)

	except Exception,e:
		print e

def decodeHTML(url):
	if url['site'] == 'btany.com':
		decodeBTmayi(url['url'])
	elif url['site'] == 'btwalk.org':
		decodeBTwalk(url['url'])
	elif url['site'] == '97ki.com':
		pass

def decodeBTmayi(url):
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	try:
		tmpreq = requests.get(url = url,headers = headers,verify = False,timeout = 20)
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

			print str(x)+' → '+realTitle

			queryList.append({"title":realTitle,"magnet":"magnet"+magnet[x],"thunder":"thunder"+thunder[x],"size":size[0]})
	except Exception,e:
		print e

def decodeBTwalk(url):
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}
	try:
		tmpreq = requests.get(url = url,headers = headers,verify = False,timeout = 20)
		htmlstr = tmpreq.content.replace('\r\n','')

		if len(htmlstr) > 10000:
			itemsDiv = re.findall(r'<div class="search-item">(.+?)</div>',htmlstr)

			titles = re.findall(r'<div class="item-title">(.+?)</div>',htmlstr)
			magnet = re.findall(r'href="magnet(.+?)"',htmlstr)
			thunder = re.findall(r'href="thunder(.+?)"',htmlstr)
			sizes = re.findall(r'文件大小：(.+?)</b>',htmlstr)

			for x in range(0,len(itemsDiv)):

				titleStr = re.findall(r'<h3>(.+?)</h3>',titles[x])[0]
				titleStr = titleStr.replace('\r\n','').replace('<b>','').replace('</b>','')
				realTitle = re.findall(r'target="_blank">(.+?)</a>',titleStr)[0]
				size = sizes[x].split('>')[1]

				print str(x)+' → '+realTitle

				queryList.append({"title":realTitle,"magnet":"magnet"+magnet[x],"thunder":"thunder"+thunder[x],"size":size})
	except Exception,e:
		print e

if __name__ == '__main__':
	global queryList
	queryList = []

	print '[*] Searching ...'
	print '[*]'+'-'*90

	# getUrlByBTmayi()
	# getUrlByBTwalk()
	getUrlBy97ki()

	print '[*]'+'-'*90
	print '[*] Finished!'
