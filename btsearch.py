#! /usr/bin/env python
#! coding=utf-8
#! author kbdancer @92ez.com

import threading
import requests
import Queue
import json
import web
import sys
import re

urls = (
	"/","index",
	"/query","queryResult"
)

render = web.template.render('templates',cache=False)

class index:
	def GET(self):
		return render.index()

def bThread(urllist):
	
	threadl = []
	queue = Queue.Queue()
	for url in urllist:
		queue.put(url)

	for x in xrange(0, 50):
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

class queryResult:
	def POST(self):

		keyword = web.input().get("keyword")

		url = "http://www.btmayi.me/search/"+ keyword +"-first-asc-1"

		try:
			req = requests.get(url=url,verify = False,timeout = 20)
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
				tmpurl = "http://www.btmayi.me/search/"+ keyword +"-first-asc-"+str(pl)
				urllist.append(tmpurl)

			global queryList
			queryList = []

			bThread(urllist)

			return json.dumps({"code":0,"rows":queryList})

		except Exception,e:
			return json.dumps({"code":-1,"msg":"exception"})
			pass


def decodeSomething(url):

	try:
		tmpreq = requests.get(url = url,verify = False,timeout = 20)
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

			queryList.append({"title":realTitle,"magnet":"magnet"+magnet[x],"thunder":"thunder"+thunder[x],"size":size[0]})

	except Exception,e:
		return json.dumps({"code":-1,"msg":"exception"})
		pass

if __name__ == '__main__':
	app = web.application(urls,globals())
	app.run()
