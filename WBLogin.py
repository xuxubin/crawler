# coding:utf-8

# 参考http://shrik3.com/2016/03/25/sina-login/的文章
# 模拟微博登录流程

import urllib2
import cookielib
import base64
import re
import json
import rsa
import urllib
import binascii

# 注意构造请求的时候要加上header
# 模拟新浪微博的登录跳转过程
class WBLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }
        self.cookie = cookielib.CookieJar()
        self.handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener = urllib2.build_opener(self.handler)

    # 用户名采用url编码再采用base64编码,之后post数据的时候要用到
    def get_encrypted_name(self):
        username_url = urllib2.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_url))
        return username_encrypted.decode('utf-8')

    # 获取json格式数据的返回
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

    # 从js代码中推断密码的加密方式
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

if __name__=='__main__':
    launcher = WBLogin('username','password')
    launcher.login()