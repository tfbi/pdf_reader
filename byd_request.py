import requests


class Request:
    def __init__(self, url, proxies=None):
        self.url = url
        self.proxies = proxies
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0",
        }

    def get(self, params=None):
        response = requests.get(url=self.url, params=params, headers=self.headers, proxies=self.proxies)
        return response.content

    def post(self, data=None):
        response = requests.post(url=self.url, data=data, headers=self.headers, proxies=self.proxies)
        return response.content
