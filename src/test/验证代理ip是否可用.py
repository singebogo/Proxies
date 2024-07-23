# _*_ coding:utf-8 _*_

import urllib2
import re


class TestProxy(object):
    def __init__(self):
        self.ip = '106.46.136.64'
        self.port = '808'
        self.url = 'http://www.baidu.com'
        self.timeout = 3

        self.regex = re.compile(r'baidu.com')

        self.run()

    def run(self):
        self.linkWithProxy()

    def linkWithProxy(self):
        server = 'http://' + self.ip + ':' + self.port

        opener = urllib2.build_opener(urllib2.ProxyHandler({'http': server}))
        urllib2.install_opener(opener)
        try:
            response = urllib2.urlopen(self.url, timeout=self.timeout)
        except:
            print('%s connect failed' % server)
            return
        else:
            try:
                str = response.read()

            except:
                print('%s connect failed' % server)
                return
            if self.regex.search(str):
                print('%s connect success .......' % server)
                print(self.ip + ':' + self.port)



if __name__ == '__main__':
    Tp = TestProxy()
