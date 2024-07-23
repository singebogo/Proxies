import json
import requests

def proxy():
    url = 'http://httpbin.org/get'
    r=requests.get(url)
    origin = json.loads(r.text)['origin']
    return origin
