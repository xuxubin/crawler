# -*- encoding=utf-8 -*-

import urllib2
import urllib

response = urllib2.urlopen("http://www.163.com")
# print response.read().decode("GBK").encode("utf-8")

request = urllib2.Request("http://www.163.com")
response = urllib2.urlopen(request)
# print response.read().decode('GBK')

url = 'http://www.zhihu.com/#signin'
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
values = {'username' : '675125417@qq.com', 'password':'135156'}
header = { 'User-Agent':user_agent}
data = urllib.urlencode(values)
request = urllib2.Request(url, data, header)
try:
    response = urllib2.urlopen(request)
except urllib2.URLError, e:
    print e.code
    print e.reason
# page = response.read()
# print page.decode('GBK')