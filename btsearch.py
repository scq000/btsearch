#! /usr/bin/env python
# ! coding=utf-8
# ! author kbdancer @92ez.com

import threading
import requests
import sqlite3
import urllib
import Queue
import math
import json
import sys
import re

reload(sys)
sys.setdefaultencoding('utf8')

# Console colors
W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green


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
    url = "http://www.btany.com/search/" + keyword + "-first-asc-1"
    print '[*] 获取 www.btany.com 基本信息...'
    try:
        req = requests.get(url=url, verify=False, headers=headers, timeout=20)
        responseStr = req.content

        # no result
        if len(responseStr.split('<span>无<b>')) > 1:
            return json.dumps({"code": -1, "msg": "can not find any page!"})
            sys.exit()

        temppage = re.findall(r'<div class="bottom-pager">(.+?)</div>', responseStr, re.S)[0].replace('\n', '')
        pagestr = re.findall(r'<a href="(.+?)">', temppage)

        if len(pagestr) < 1:
            # only one page
            maxpage = 1
        else:
            maxpage = int(re.findall(r'<a href="(.+?)">', temppage)[-1].split('asc-')[1])

        urllist = []

        for pl in range(1, maxpage + 1):
            tmpurl = {"site": "btany.com", "url": "http://www.btany.com/search/" + keyword + "-first-asc-" + str(pl)}
            urllist.append(tmpurl)

        bThread(urllist)

    except Exception, e:
        print e


def getUrlByBTwalk():
    keyword = sys.argv[1]
    url = "http://www.btmeet.net/search/" + keyword + "/1-1.html"
    print '[*] 获取 www.btmeet.net 基本信息...'
    try:
        req = requests.get(url=url, verify=False, headers=headers, timeout=20)
        responseStr = req.content.replace('\r\n', '')

        totalCount = int(re.findall(r'<span>大约 (.+?) 条结果', responseStr)[0])
        totalPage = int(math.ceil(float(totalCount) / 10))

        urllist = []
        for pl in range(1, totalPage + 1):
            tmpurl = {"site": "btmeet.net","url": "http://www.btmeet.net/search/" + keyword + "/" + str(pl) + "-1.html"}
            urllist.append(tmpurl)

        bThread(urllist)

    except Exception, e:
        print e


def decodeHTML(url):
    if url['site'] == 'btany.com':
        decodeBTmayi(url['url'])
    elif url['site'] == 'btmeet.net':
        decodeBTwalk(url['url'])


def decodeBTmayi(url):
    print '[*] 正在解析 '+ url + ' 的数据...'
    try:
        tmpreq = requests.get(url=url, headers=headers, verify=False, timeout=20)
        htmlstr = tmpreq.content

        magnet = re.findall(r'href="magnet(.+?)"', htmlstr)
        thunder = re.findall(r'href="thunder(.+?)"', htmlstr)
        title = re.findall(r'<div class="item-list">(.+?)</div>', htmlstr, re.S)

        for x in range(0, len(magnet)):
            tempTtitle = title[x].replace('<span class="highlight">', '').replace('</span>', '').replace('\n', ' ')
            size = re.findall(r'<span>(.+?)</p>', tempTtitle)
            titleText = re.findall(r'<p>(.+?)<span>', tempTtitle)

            # to fix some ad script
            trashcode = re.findall(r'<a(.+?)script>', titleText[0])

            if len(trashcode) > 0:
                trashTitle = titleText[0]
                for t in range(0, len(trashcode)):
                    trashTitle = trashTitle.replace('<a' + trashcode[t] + 'script>', "")
                realTitle = trashTitle
            else:
                realTitle = titleText[0]

            resData = {"title": realTitle, "magnet": "magnet" + magnet[x], "thunder": "thunder" + thunder[x],"size": size[0]}
            queryList.append(resData)
    except Exception, e:
        print e


def decodeBTwalk(url):
    print '[*] 正在解析 ' + url + ' 的数据...'
    try:
        tmpreq = requests.get(url=url, headers=headers, verify=False, timeout=20)
        htmlstr = tmpreq.content.replace('\r\n', '')

        if len(htmlstr) > 10000:
            itemsDiv = re.findall(r'<div class="search-item">(.+?)</div>', htmlstr)
            titles = re.findall(r'<div class="item-title">(.+?)</div>', htmlstr)
            sizes = re.findall(r'文件大小：(.+?)</b>', htmlstr)

            for x in range(0, len(itemsDiv)):
                titleStr = re.findall(r'<h3>(.+?)</h3>', titles[x])[0]
                titleStr = titleStr.replace('\r\n', '').replace('<b>', '').replace('</b>', '')
                titleStr = re.findall(r'decodeURIComponent\((.+?)\)\);', titleStr)[0].replace('"+"','').replace('"','')
                realTitle = urllib.unquote(titleStr).replace('<b>','').replace('</b>','')
                size = sizes[x].split('>')[1]

                detialUrl = 'http://www.btmeet.net' + re.findall(r'<a href="(.+?)" target="', titles[x])[0]
                print '[*] 正在解析 ' + detialUrl + ' 的数据...'
                detialStr = requests.get(detialUrl, timeout=10).content
                magnet = re.findall(r'href="magnet(.+?)"', detialStr)[0]
                thunder = re.findall(r'href="thunder(.+?)"', detialStr)[0]

                resData = {"title": realTitle, "magnet": "magnet" + magnet, "thunder": "thunder" + thunder,"size": size}
                queryList.append(resData)

    except Exception, e:
        print e


def clearDB():
    print '[*] 清空上一次的采集数据...'
    try:
        cx = sqlite3.connect(sys.path[0]+"/search.db")
        cx.text_factory = str
        cu = cx.cursor()
        cu.execute("delete from `record`")
        cu.execute("update sqlite_sequence SET seq = 0 where name ='record'")
        cx.commit()
        cu.close()
        cx.close()
    except Exception, e:
        print e


def saveToDB():
    print '[*] 开始存储数据到数据库...'
    saveCount = 0
    try:
        cx = sqlite3.connect(sys.path[0] + "/search.db")
        cx.text_factory = str
        cu = cx.cursor()
        print len(queryList)
        for m in queryList:
            cu.execute("select * from record where magnet='%s' or thunder='%s'" % (m['magnet'], m['thunder']))
            if not cu.fetchone():
                cu.execute("insert into record (title,magnet,thunder,size) values (?,?,?,?)",(m['title'], m['magnet'], m['thunder'], m['size']))
                cx.commit()
                print '[√] => Insert successly!'
                saveCount = saveCount + 1
            else:
                print R+'[x] <= Found in database!'+W
        cu.close()
        cx.close()

        print '*'*60
        print '[√] 数据采集完成，共采集%s条' % str(len(queryList))
        print '[√] 数据存储完成，共存储%s条' % saveCount
    except Exception, e:
        print e


if __name__ == '__main__':
    global queryList
    global headers

    queryList = []
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"}

    print '[*] Searching ...'
    print '[*]' + '-' * 60

    getUrlByBTmayi()
    getUrlByBTwalk()
    clearDB()
    saveToDB()


