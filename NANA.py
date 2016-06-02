# coding:UTF-8

import urllib2
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from bs4 import BeautifulSoup

class NANA:
    def __init__(self, wb_id):
        self.url = 'http://photo.weibo.com/'+str(wb_id)+'/talbum/index#!/mode/1/page/'
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.112 Safari/537.36'
        self.headers = {'User-Agent':self.userAgent,'Connection':'keep-alive',}
        self.driver = webdriver.Chrome()
        self.pageIdx = 1
        self.maxIdx = 1
        self.fileHelper = FileHelper()
        self.imgIdx = 1

    # 使用新浪通行证登录获得cookie
    def login(self, username, pwd):
        self.driver.get('http://login.sina.com.cn/')
        username_ele = self.driver.find_element_by_id('username')
        pwd_ele = self.driver.find_element_by_id('password')
        username_ele.send_keys(username)
        pwd_ele.send_keys(pwd, Keys.RETURN)
        time.sleep(5)  # 等待一段时间使得页面加载完成

    # 获取某一页的html代码
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

    # 从html代码中匹配相片链接
    def getPageItem(self, content):
        if not content:
            print '页面加载失败'

        #最大页码
        page_pattern = re.compile('<a href=.*?"pageTo" action-data="page=([0-9].*?)">.*?</a>')
        pages = re.findall(page_pattern, content)
        # 更新最大页码
        pages_int = [int(x) for x in pages]
        self.maxIdx = max(pages_int)

        # 两个链接,时间,微博内容
        # 不使用正则表达式
        # img_pattern = re.compile('<li>.*?<dl class="m_photoItem m_photoItem_a phtItem_hv">.*?<a href="(.*?)">.*?' +
        #                          '<img src="(.*?)".*?/>.*?</a>.*?<span node-type="time">(.*?)</span>.*?' +
        #                          '<p title="(.*?)" class.*?</p>.*?</dd>.*?</dl></li>',re.S)
        # items = re.findall(img_pattern, content)
        html_tree = BeautifulSoup(content)
        html_tree.prettify()
        photo_list = html_tree.find_all("dl", class_="m_photoItem m_photoItem_a phtItem_hv")
        items = []
        for photo_item in photo_list:
            item = {}
            item["detail_page"] = photo_item.find('dt').find('a')["href"]
            item["small_img_link"] = photo_item.find('dt').find('a').find('img')["src"]
            item["time"] = photo_item.find('dd').find("span", attrs={"node-type":"time"}).string
            try:
                item["description"] = photo_item.find('dd').find_all("p")[-1].get("title")
            except:
                item["description"] = None
            items.append(item)

        return items


    def savePageImg(self, items):
        # self.fileHelper.openFile('urls_wife.txt','a')
        for item in items:
            big_img_url = re.sub('/small/', '/mw690/', item["small_img_link"]) #转成大图的链接
            parts = big_img_url.split('/')
            parts = parts[-1].split('.')
            self.fileHelper.saveImg(big_img_url,str(self.imgIdx)+'.'+parts[-1])
            self.imgIdx = self.imgIdx + 1
            # self.fileHelper.fp.write(big_img_url+'\n')
            # time.sleep(1)
        # self.fileHelper.closeFile()

    def saveAllImg(self):
        while self.pageIdx <= self.maxIdx:
            self.savePageImg(self.pageIdx)
            time.sleep(3)
        print 'finish page %d' % self.pageIdx

    def close(self):
        time.sleep(20)
        self.driver.close()


class FileHelper:
    # 创建目录
    def __init__(self):
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.112 Safari/537.36'
        self.headers = {'User-Agent':self.userAgent,'Connection':'keep-alive'}
        self.path = '/Users/user/Downloads/yifu2'
        self.fp = None
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def saveImg(self, imgurl, fileName):
        # 伪装成浏览器
        request = urllib2.Request(imgurl, headers =self.headers)
        filepath = self.path + fileName
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            fp = open(filepath, 'wb')
            fp.write(data)
            print 'save img %s' % filepath
            fp.close()
        except:
            print 'save img %s fail' % filepath

    def openFile(self, fileName, mode):
        self.fp = open(self.path+fileName, mode)

    def closeFile(self):
        self.fp.close()


if __name__=='__main__':

    wb_id = raw_input('Please input the id of album owner:')
    nana = NANA(wb_id)

    user_name = raw_input('Please input the your username:')
    password = raw_input('Please input your weibo password:')

    nana.login(user_name, password)

    nana.getPage(nana.pageIdx)
    time.sleep(1)

    # 通过点击下一页的按钮来进入下一页
    while True:
        items = nana.getPageItem(nana.driver.page_source)
        nana.savePageImg(items)
        print "finish page %d" % nana.pageIdx
        nana.pageIdx += 1
        if nana.pageIdx > nana.maxIdx:
            break
        try:
            next_btn = nana.driver.find_element_by_class_name('next')
            next_btn.click()
            time.sleep(3)
        except:
            print 'next page error'

    print "finish download img"
    nana.close()