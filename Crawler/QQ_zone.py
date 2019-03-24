# -*- coding:utf-8 -*-
"""
@author:zyl
@file:qq_crawler.py
@time:2019/3/16 10:28
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import random
import requests
from urllib import parse
class QQ_Spider(object):
    def __init__(self,user,password):
        '''
        初始化
        '''
        print("系统正在初始化...")
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.driver_zone = webdriver.Chrome(executable_path='E:\Office worke\chormedrive\chromedriver.exe',options=self.chrome_options)# 需安装chormediver 注意版本对应 若是firefox 则应下载对应驱动
        self.driver_zone.get('https://i.qq.com/')
        self.driver_mail = webdriver.Chrome(executable_path="E:\Office worke\chormedrive\chromedriver.exe",options=self.chrome_options)
        self.driver_mail.get('https://mail.qq.com/')
        self.__username = user#输入你的QQ号
        self.__password = password #输入你的密码
        self.req = requests.Session()  #保持会话
        self.qq_num=[] #初始化要爬取的qq列表
        print("系统初始化完成...")
    def QQ_zone_login(self):
        '''
        登录、调用get_g_tk()函数
        :return:
        '''
        print("模块运行中...")
        self.driver_zone.switch_to.frame('login_frame')
        self.element = self.driver_zone.find_element_by_id('switcher_plogin')
        if self.element.is_displayed():
            self.driver_zone.find_element_by_id('switcher_plogin').click()
        self.driver_zone.find_element_by_id('u').clear()
        self.driver_zone.find_element_by_id('u').send_keys(self.__username)
        self.driver_zone.find_element_by_id('p').clear()
        self.driver_zone.find_element_by_id('p').send_keys(self.__password)
        self.driver_zone.find_element_by_id('login_button').click()
        time.sleep(0.8) #等待浏览器加载
        self.driver_zone.get('http://user.qzone.qq.com/{}'.format(self.__username))
        #cookie = ''
        self.cookie_zone = {}
        cookie_zone={}
        for item in self.driver_zone.get_cookies():
            #cookie += item["name"] + '=' + item['value'] + ';'  #拼接cookie 为字符串
            cookie_zone[item["name"]]=item['value']  #拼接cookie为字典

        self.cookie_zone = cookie_zone
        self.get_g_tk()
        #self.headers['Cookie'] = self.cookies
        self.driver_zone.quit()

    def QQ_mail_login(self):
        self.driver_mail.switch_to.frame('login_frame')  # 登录在该frame内
        self.element=self.driver_mail.find_element_by_id('switcher_plogin')
        if self.element.is_displayed():  #判断该切换按钮是否存在
            self.driver_mail.find_element_by_id('switcher_plogin').click()
        self.driver_mail.find_element_by_id('u').clear()
        self.driver_mail.find_element_by_id('u').send_keys(self.__username)
        self.driver_mail.find_element_by_id('p').clear()
        self.driver_mail.find_element_by_id('p').send_keys(self.__password)
        self.driver_mail.find_element_by_id('login_button').click()
        time.sleep(0.8)
        self.driver_mail.get(
            'https://mail.qq.com/cgi-bin/readtemplate?check=false&t=loginpage_new_jump&vt=passport&vm=wpt&ft=loginpage&target=&account={}'.format(
                self.__username))
        # cookie={}
        cookie_mail = ''
        for item in self.driver_mail.get_cookies():
            cookie_mail += item["name"] + '=' + item['value'] + ';'  # 拼接cookie 为字符串
        # cookie[item["name"]] = item['value']
        self.cookie_mail=cookie_mail
        self.driver_mail.quit()
        # print(cookie)
    def get_qq_num(self):
        print('输入你要爬取的目标好友qq，可以输入多个，以回车隔开，以0结束')
        while(1):
            qq=input()
            if qq is not '0':
                self.qq_num.append(qq)
            else:
                break
    def get_QQgroup(self):
        print("模块初始化...")
        url = "https://mail.qq.com/cgi-bin/login?vt=passport&vm=wpt&ft=loginpage&target="
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://mail.qq.com/',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
            , 'cookie': self.cookie_mail
        }
        session = requests.Session()
        res = session.post(url=url, headers=headers, allow_redirects=False)
        location = res.headers['location']
        sid = location[location.find('sid=') + 4:location.find('&', location.find('sid='))]
        url2 = 'https://mail.qq.com/cgi-bin/laddr_lastlist?' + 'sid=' + sid + '&encode_type=js&t=addr_datanew&s=AutoComplete&category=hot&resp_charset=UTF8&ef=js&r=0.010669463067699336'  # r的值为18位随机数,可以写死
        header = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie_mail,
            'referer': 'https://mail.qq.com/zh_CN/htmledition/ajax_proxy.html?mail.qq.com&v=140521',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        requ = requests.get(url=url2, headers=header)
        text=requ.text[1:len(requ.text) - 1]  # 去除源数据中的圆括号
        qq_groups = text[text.find('qqgroups : ') + 11:text.find(',groups :', text.find(
            'qqgroups : '))]  # 截取qqgroups那一块数据
        qq_groups = re.sub(re.compile('."\0"'), '', qq_groups)  # 除去空字符，防止eval函数报错 该函数不能处理空字符
        qq_groups = eval(qq_groups)  # 将字符串转为list
        print("初始化完成...")
        for item in qq_groups:
            print(str(int(item[0]) - 1000000) + ' : ' + item[2])  # 显示分组
        in_list = []
        print('请选择你要爬取的分组(输入对应分组的索引,可输入多个，以-1结束):')
        while (1):
            i = int(input())
            if i is not -1:
                in_list.append(i)
            else:
                break
        for i in in_list:
            for num in qq_groups[i][1]:
                self.qq_num.append(str(num))
        #print(self.qq_num)
    def mode_choose(self):
        mode = int(input("请选择爬取模式：1：指定QQ 2：指定分组 3：混合模式"))
        if mode is 1:
            self.get_qq_num()
        elif mode is 2:
            self.get_QQgroup()
        else:
            self.get_qq_num()
            self.get_QQgroup()
    def get_g_tk(self):
        '''
        获取g_tk()
        '''
        #p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))] #若拼接为字符串则使用该方法寻找p_skey find函数返回的是指定目标在字符串中的索引
        p_skey=self.cookie_zone['p_skey']
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        self.g_tk = h & 2147483647

    def get_info(self):
        '''
        构造说说请求链接
        正则解析
        '''
        url = 'https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
        params = {
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'sort': 0,
            'num': 20,
            'repllyunm': 100,
            'cgi_host': 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
            'callback': '_preloadCallback',
            'code_version': 1,
            'format': 'jsonp',
            'need_private_comment': 1,
            'g_tk': self.g_tk
        }
        headers = {
            'host': 'h5.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'connection': 'keep-alive'
        }
        url = url + parse.urlencode(params)
        for q in self.qq_num:
            t1, pos = True, 0
            url_ = url + '&uin=' + str(q)
            while(t1):
                url__ = url_ + '&pos=' + str(pos)
                info = self.req.get(url=url__, headers=headers,cookies=self.cookie_zone)
                if '\"msglist\":null' in info.text or "\"message\":\"对不起,主人设置了保密,您没有权限查看\"" in info.text:
                    t1 = False
                    if '\"message\":\"对不起,主人设置了保密,您没有权限查看\"' in info.text:
                        print("对不起,主人设置了保密,您没有权限查看")

                else:
                    created_time = re.findall('created_time":\d+', info.text)
                    contents = re.findall('],"content":".*?"', info.text)
                    comment_content = re.findall('commentlist":(null|.*?],)', info.text)
                    comments = re.findall('cmtnum":\d+', info.text)
                    remove_emotion=re.compile('\[em\].*?]')
                    for _time,  _content, _comment_content, _comment in \
                            zip(created_time,  contents, comment_content, comments):
                        _comment_content=re.sub(remove_emotion,'',_comment_content)
                        _content = re.sub(remove_emotion, '', _content)
                        data = {
                            'QQ':str(q),
                            'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(re.sub('created_time":', '', _time)))),
                            'content': re.sub('],"content":"|"', '', _content),
                            'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(re.sub('content":"|"', '', x), re.sub('createTime2":"|"', '', y), re.sub('name":"|"', '', z), re.sub('uin":', '', zz)) for x, y, z, zz in zip(re.findall('content":".*?"', _comment_content), re.findall('createTime2":".*?"', _comment_content), re.findall('name":".*?"', _comment_content), re.findall('uin":\d+', _comment_content))]),
                            'comment': re.sub('cmtnum":', '', _comment),
                        }
                        with open('QQinfo.txt', 'a', encoding='utf-8') as f:
                            f.write(str(data) + "\n")
                            f.close()
                            print("写入成功")
                    pos += 20
                    time.sleep(random.uniform(4.5, 5.5))
if __name__ == '__main__':
    user=input('请输入账号: ')
    password=input('请输入密码: ')
    qq_zone_crawler = QQ_Spider(user,password)
    qq_zone_crawler.QQ_zone_login()
    qq_zone_crawler.QQ_mail_login()
    qq_zone_crawler.mode_choose()
    qq_zone_crawler.get_info()
