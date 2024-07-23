import requests
from bs4 import BeautifulSoup


# 1. 获取代理IP列表
def get_proxy_list():
    # 构造请求头，模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    # 请求代理IP网页
    url = "http://www.zdopen.com/ShortProxy/GetIP/?api&akey&timespan=5&type=1"
    response = requests.get(url, headers=headers)

    # 解析网页获取代理IP列表
    soup = BeautifulSoup(response.text, "html.parser")
    proxy_list = []
    table = soup.find("table", {"id": "ip_list"})
    for tr in table.find_all("tr"):
        td_list = tr.find_all("td")
        if len(td_list) > 0:
            ip = td_list[1].text.strip()
            port = td_list[2].text.strip()
            type = td_list[5].text.strip()
            proxy_list.append({
                "ip": ip,
                "port": port,
                "type": type
            })
    return proxy_list


# 2. 验证代理IP可用性
def verify_proxy(proxy):
    # 构造请求头，模拟浏览器请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }

    # 请求目标网页并判断响应码
    url = "http://www.baidu.com"
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False


# 3. 测试代理IP列表可用性
def test_proxy_list(proxy_list):
    valid_proxy_list = []
    for proxy in proxy_list:
        if verify_proxy(proxy):
            valid_proxy_list.append(proxy)
    return valid_proxy_list


# 4. 使用代理IP发送请求
def send_request(url, headers, proxy):
    # 发送请求并返回响应结果
    response = requests.get(url, headers=headers, proxies=proxy)
    return response.text


# 程序入口
if __name__ == "__main__":
    # 获取代理IP列表
    proxy_list = get_proxy_list()

    # 验证代理IP可用性
    valid_proxy_list = test_proxy_list(proxy_list)

    # 输出可用代理IP
    print("有效代理IP列表：")
    for proxy in valid_proxy_list:
        print(proxy)

    # 使用代理IP发送请求
    url = "http://www.baidu.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    proxy = {
        "http": "http://" + valid_proxy_list[0]["ip"] + ":" + valid_proxy_list[0]["port"],
        "https": "https://" + valid_proxy_list[0]["ip"] + ":" + valid_proxy_list[0]["port"]
    }
    response = send_request(url, headers, proxy)
    print(response)