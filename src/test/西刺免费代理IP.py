import requests
import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
URLS = [
    'https://www.xicidaili.com/nn/',
    'https://www.xicidaili.com/nt/',
    'https://www.xicidaili.com/wn/',
    'https://www.xicidaili.com/wt/'
]

def get_proxies(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find('table', id='ip_list').find_all('tr')[1:]
    proxies = []
    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[1].text.strip()
        port = tds[2].text.strip()
        protocol = tds[5].text.strip().lower()
        if protocol in ('http', 'https'):
            proxy = protocol + '://' + ip + ':' + port
            proxies.append(proxy)
    return proxies

def check_proxy_alive(proxy):
    try:
        protocol = 'https' if 'https' in proxy else 'http'
        url = protocol + '://www.baidu.com'
        session = requests.session()
        session.proxies = {protocol: proxy}
        session.get(url, headers=HEADERS, timeout=(5, 10))
        print(f'{proxy} is valid')
        return True
    except Exception:
        return False

def validate_proxies(proxies):
    valid_proxies = set()
    with ThreadPoolExecutor(max_workers=20) as executor:
        for res, proxy in zip(executor.map(check_proxy_alive, proxies), proxies):
            if res:
                valid_proxies.add(proxy)
    return valid_proxies

if __name__ == '__main__':
    proxies = []
    for url in URLS:
        print(f'Getting proxies from {url}...')
        proxies += get_proxies(url)
    print(f'Total proxies: {len(proxies)}')

    valid_proxies = validate_proxies(proxies)
    print(f'Valid proxies: {len(valid_proxies)}')
    print('Validation finished at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))