import logging
import json
import requests

logger = logging.Logger("fileAndConsole")


def host_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def origin_ip():
    url = 'http://httpbin.org/get'
    r=requests.get(url)
    origin = json.loads(r.text)['origin']
    return origin

def check_proxy(url, ip, port):
    """第二种："""
    try:
        # 设置重连次数
        requests.adapters.DEFAULT_RETRIES = 3
        # IP = random.choice(IPAgents)
        proxy = f"http://{ip}:{port}"
        # thisIP = "".join(IP.split(":")[0:1])
        # print(thisIP)
        res = requests.get(url=url, timeout=5, proxies={"http": proxy})
        proxyIP = res.text
        if proxyIP == proxy:
            logger.info("代理IP:'" + proxyIP + "'有效！")
            return True
        else:
            logger.info("2代理IP无效！")
            return False
    except Exception as e:
        logger.info("1代理IP无效！", e)
        return False


def domestic(ip, port):
    return check_proxy("http://www.baidu.com/", ip, port)

def abroad(ip, port):
    return check_proxy("http://www.google.com/", ip, port)

if __name__ == '__main__':
    host_ip()