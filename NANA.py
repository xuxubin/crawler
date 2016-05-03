# coding:UTF-8

import urllib2
import urllib
import base64
import re
import json
import rsa
import binascii
import cookielib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os

# 注意构造请求的时候要加上header
# 模拟新浪微博的登录跳转过程
class Launcher:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }
        self.cookie = cookielib.CookieJar()
        self.handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)


    def get_encrypted_name(self):
        username_url = urllib2.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_url))
        return username_encrypted.decode('utf-8')

    def get_prelogin_params(self):
        pattern = re.compile('\((.*)\)')
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&' +\
              self.get_encrypted_name() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)'
        try:
            request = urllib2.Request(url)
            response = self.opener.open(request)
            raw_data = response.read().decode('utf-8')
            json_data = pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except urllib2.error as e:
            print("%d"%e.code)
            return None

    def get_encrypted_pwd(self, data):
        rsa_e = 65537
        pw_str = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.password)
        key = rsa.PublicKey(int(data['pubkey'],16),rsa_e)
        pw_encypted = rsa.encrypt(pw_str.encode('utf-8'), key)
        self.password = ''   #安全起见清空明文密码
        passwd = binascii.b2a_hex(pw_encypted)
        return passwd

    def build_post_data(self,raw):
        post_data = {
            "entry":"weibo",
            "gateway":"1",
            "from":"",
            "savestate":"7",
            "useticket":"1",
            "pagerefer":"http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf":"1",
            "su":self.get_encrypted_name(),
            "service":"miniblog",
            "servertime":raw['servertime'],
            "nonce":raw['nonce'],
            "pwencode":"rsa2",
            "rsakv":raw['rsakv'],
            "sp":self.get_encrypted_pwd(raw),
            "sr":"1280*800",
            "encoding":"UTF-8",
            "prelt":"77",
            "url":"http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype":"META"
        }
        data = urllib.urlencode(post_data).encode('utf-8')
        return data

    def login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        data = self.get_prelogin_params()
        post_data = self.build_post_data(data)

        try:
            request = urllib2.Request(url=url,data=post_data,headers=self.headers)
            response = self.opener.open(request)
            html = response.read().decode('GBK')
            '''
            一开始用的是utf－8解码，然而得到的数据很丑陋，却隐约看见一个GBK字样。所以这里直接采用GBK解码
            '''
            # print(html)

        except urllib2.URLError as e:
            print(e.code)

        p = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"userdomain":"(.*?)"')
        try:
            login_url = p.search(html).group(1)
            request = urllib2.Request(login_url, headers = self.headers)
            response = self.opener.open(request)
            page = response.read().decode('utf-8')
            # print page
            login_url = 'http://weibo.com/' + p2.search(page).group(1)
            request = urllib2.Request(login_url, headers = self.headers)
            response = self.opener.open(request)
            final_loc = response.url
            final = response.read().decode('utf-8')
            # print final
        except urllib2.URLError as e:
            print e.reason

    def get_album(self, idx):
        url = 'http://photo.weibo.com/1780481403/talbum/index#!/mode/1/page/'
        url = url + str(idx)
        request = urllib2.Request(url, headers=self.headers)
        response = self.opener.open(request)
        album_page = response.read()
        print album_page

class NANA:
    def __init__(self):
        self.url = 'http://photo.weibo.com/1780481403/talbum/index#!/mode/1/page/'
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.112 Safari/537.36'
        self.headers = {'User-Agent':self.userAgent,'Connection':'keep-alive',}
        self.driver = webdriver.Chrome()
        self.pageIdx = 1
        self.maxIdx = 1
        self.fileHelper = FileHelper();

    def login(self, username, pwd):
        self.driver.get('http://login.sina.com.cn/')
        username_ele = self.driver.find_element_by_id('username')
        pwd_ele = self.driver.find_element_by_id('password')
        username_ele.send_keys(username)
        pwd_ele.send_keys(pwd, Keys.RETURN)
        time.sleep(5)

    def getPage(self, idx):
        try:
            url = self.url + str(idx)
            self.driver.get(url)
            time.sleep(1) #需要加一些延时使得js代码可以执行
            content = self.driver.page_source
            return content
        except:
            print u"连接失败"
            return None

    def getPageItem(self, idx):
        content = self.getPage(idx)
        if not content:
            print '页面加载失败'

        page_pattern = re.compile('<a href=.*?"pageTo" action-data="page=([0-9].*?)">.*?</a>')

        img_pattern = re.compile('<li>.*?<dl class="m_photoItem m_photoItem_a phtItem_hv">.*?<a href="(.*?)">.*?<img src="(.*?)".*?/>'+
                         '.*?</a>',re.S)
        items = re.findall(img_pattern, content)

        pages = re.findall(page_pattern, content)
        # 更新最大页码
        pages_int = [int(x) for x in pages]
        self.maxIdx = max(pages_int)
        return items

    def savePageImg(self, idx):
        items = self.getPageItem(idx)
        for item in items:
            big_img_url = re.sub('/small/', '/mw690/', item[1])
            parts = item[1].split('/')
            self.fileHelper.saveImg(big_img_url,parts[-1])

    def close(self):
        self.driver.close()


class FileHelper:
    # 创建目录
    def __init__(self):
        self.path = '/Users/user/Downloads/yifu'
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def saveImg(self, imgurl, fileName):
        response = urllib2.urlopen(imgurl)
        data = response.read()
        filepath = self.path + fileName
        fp = open(filepath, 'wb')
        fp.write(data)
        print 'save img %s' % filepath
        fp.close()


if __name__=='__main__':
    # launcher = Launcher('675125417@qq.com','Liyuan201')

    nana = NANA()
    nana.login('675125417@qq.com','Liyuan201')

    nana.savePageImg(1)
    print "print"
    nana.close()