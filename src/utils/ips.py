import json
import logging
import re
from threading import Thread

import requests
import chardet
import traceback
from lxml import etree
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

from .ip_check import domestic, abroad
from .slite import executemany_sql
logger = logging.getLogger('fileAndConsole')


"""
66代理	http://www.66ip.cn/
西刺代理	https://www.xicidaili.com
全网代理	http://www.goubanjia.com
云代理	http://www.ip3366.net
IP海	http://www.iphai.com
快代理	https://www.kuaidaili.com
免费代理IP库	http://ip.jiangxianli.com
"""

class Downloader(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        self.urls = [
            'https://www.kuaidaili.com/free/fps/',
            'https://www.kuaidaili.com/free/dps/',
        ]

    def download(self, url):
        logger.info('正在下载页面：{}'.format(url))
        try:
            resp = requests.get(url, headers=self.headers)
            resp.encoding = chardet.detect(resp.content)['encoding']

            if resp.status_code == 200:
                html = resp.text
                # return self.xpath_parse(resp.text)
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(html, 'html.parser')
                return self.script_parse(soup)

            else:
                raise ConnectionError
        except Exception:
            logger.info('下载页面出错：{}'.format(url))
            traceback.print_exc()

    def xpath_parse(self, resp):
        try:
            page = etree.HTML(resp)
            trs = page.xpath('//div[@id="table__free-proxy"]/div/table/tbody/tr')
            proxy_list = []
            for tr in trs:
                ip = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                proxy = {
                    'proxy': ip + ':' + port
                }
                proxy_list.append(proxy)
            return proxy_list
        except Exception:
            logger.error('解析IP地址出错')
            traceback.print_exc()

    def script_parse(self, soup):
        # 查找所有的script标签
        scripts = soup.find_all('script')
        fpsList = []
        totalCount = 0
        # 遍历每个script标签
        for script in scripts:
            # 判断script标签是否包含变量定义
            if script.string and script:
                if "fpsList" in script.string:
                    # print(script.string)
                    # 获取变量名和变量值
                    searchObj = re.search(r'const fpsList = (.*?);', script.string, re.M | re.I)
                    totalCountObj = re.search(r"let totalCount = '(.*?)';", script.string, re.M | re.I)
                    if searchObj:
                        for group in searchObj.groups():
                            fpsList.append(group)
                    if totalCountObj:
                        totalCount = totalCountObj.groups()[0]
        return fpsList, totalCount

    def run(self):
        # 初始化数据库
        for url in self.urls:
            t1 = Thread(target=self.kuaidaili_ip_today, args=(url,))
            t1.daemon = True  # 设置p1为守护进程
            t1.start()

    def kuaidaili_ip_today(self, url):
        logger.info(url)
        fpsList, totalCount = self.download(url + '{}/'.format(1))
        self.jsonf(fpsList[0])
        return totalCount, url

    def kuaidaili_ip_all(self, url):
        totalCount, url = self.kuaidaili_ip_today(url)
        count = int(int(totalCount) / 12) + 1 if int(totalCount) % 12 > 0 else int(int(totalCount) / 12)
        with ThreadPoolExecutor(max_workers=8) as t:
            obj_list = []

            for page in range(2, count):
                obj = t.submit(self.spider, url, page)
                obj_list.append(obj)

    def spider(self, url, page):
        fpsList, totalCount = self.download(url + '{}/'.format(page))
        self.jsonf(fpsList[0])

    def jsonf(self, ips):
        jips = json.loads(ips)

        # 存入数据库
        self.dbs(jips)
        with ThreadPoolExecutor(max_workers=8) as t:
            obj_list = []
            for ip in jips:
                obj = t.submit(self.check_ips, ip)
                obj_list.append(obj)

    def check_ips(self, ip):
        invaild_domestic = domestic(ip['ip'], ip["port"])
        invaild_abroad = abroad(ip['ip'], ip["port"])
        data = [(str(ip['ip']), str(ip["port"]), str(ip['last_check_time']), str(ip['speed']), str(ip['location']),
         invaild_domestic, invaild_abroad)]
        logger.info(data)
        executemany_sql(data)

    def files(self, jips):
        # 文件处理
        for ip in jips:
            with open('ips.txt', 'a+') as f:
                f.write("IP: " + str(ip['ip']) + " port: " + str(ip["port"]) + " last_check_time: "
                        + str(ip['last_check_time']) + " speed: " + str(ip['speed']) + " location: " + str(ip['location'] + '\n'))
                f.flush()
                f.close()

    def dbs(self, jips):
        data = []
        for ip in jips:
            logger.info(
                (str(ip['ip']), str(ip["port"]), str(ip['last_check_time']), str(ip['speed']), str(ip['location']), 0, 0))
            data.append(
                (str(ip['ip']), str(ip["port"]), str(ip['last_check_time']), str(ip['speed']), str(ip['location']), 0, 0))
        executemany_sql(data)