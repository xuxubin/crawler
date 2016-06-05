# -*- coding:utf-8 -*-

# 爬取糗事百科的内容,不需要登录
import urllib2
import re

class QSBK:
    def __init__(self):
        self.pageIndex = 1
        # 加上header,模拟浏览器
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/49.0.2623.112 Safari/537.36'
        self.headers = {'User-Agent':self.userAgent}
        self.stories = []
        self.enable = False

    # 获取某一页面的所有HTML内容
    def getPage(self, idx):
        try:
            url = 'http://www.iushibaike.com/hot/page/' + str(idx)
            request = urllib2.Request(url, headers =self.headers)
            request.add_header('Host','www.qiushibaike.com')
            response = urllib2.urlopen(request)
            content = response.read().decode('utf-8')
            return content
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接糗事百科失败,错误原因%s" % e.reason
                return None

    # 获取某一页面的所有段子
    def getPageItems(self, idx):
        content = self.getPage(idx)
        if not content:
            print "页面加载失败...."
            return None
        pattern = re.compile('<div class="author clearfix">.*?<h2>(.*?)</h2>.*?<div class="content">(.*?)'+
                             '</div>(.*?)<span class="stats-vote">.*?<i class="number">(.*?)</i>.*?' +
                             '<span class="stats-comments">.*?<i class="number">(.*?)</i>',re.S)
        items = re.findall(pattern, content)
        pageStories = []

        for item in items:
            haveImg = re.search("img", item[2])
            if  not haveImg:
                text = re.sub('<br/>', '\n', item[1])
                pageStories.append([item[0].strip(),text.strip(),item[3].strip(),item[4].strip()])
        return pageStories

    def loadPage(self):
        #如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                #将该页的段子存放到全局list中
                if pageStories:
                    self.stories.append(pageStories)
                    #获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    def getOneStory(self,pageStories,page):
        #遍历一页的段子
        for story in pageStories:
            #等待用户输入
            input = raw_input()
            #每当输入回车一次，判断一下是否要加载新页面
            self.loadPage()
            #如果输入Q则程序结束
            if input == "Q":
                self.enable = False
                return
            print u"第%d页\n发布人:%s\n内容:%s\n赞:%s\n" %(page,story[0],story[1],story[3])

    def start(self):
        print u"正在读取糗事百科,按回车查看新段子，Q退出"
        #使变量为True，程序可以正常运行
        self.enable = True
        #先加载一页内容
        self.loadPage()
        #局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories)>0:
                #从全局list中获取一页的段子
                pageStories = self.stories[0]
                #当前读到的页数加一
                nowPage += 1
                #将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                #输出该页的段子
                self.getOneStory(pageStories,nowPage)


if __name__=='__main__':
    spider = QSBK()
    spider.start()