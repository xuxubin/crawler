# -*- coding:utf-8 -*-

import urllib
import urllib2
import re

page = 1
url = 'http://www.qiushibaike.com/hot/page/' + str(page)
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.112 Safari/537.36'
headers = { 'User-Agent' : user_agent }
try:
    request = urllib2.Request(url, headers = headers)
    request.add_header('Host','www.qiushibaike.com')
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')

    pattern = re.compile('<div class="author clearfix">.*?<h2>(.*?)</h2>.*?<div class="content">(.*?)'+
                         '</div>(.*?)<span class="stats-vote">.*?<i class="number">(.*?)</i>.*?' +
                         '<span class="stats-comments">.*?<i class="number">(.*?)</i>',re.S)
    items = re.findall(pattern, content)
    for item in items:
        print item[0],item[1],item[2],item[3],item[4]
except urllib2.URLError, e:
    if hasattr(e, "code"):
        print e.code
    if hasattr(e, "reason"):
        print e.reason
