import os
import ssl
import requests
import nest_asyncio
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


nest_asyncio.apply()

class SSLAdapter(HTTPAdapter):
    '''An HTTPAdapter that uses an SSL context with custom ciphers.'''
    def __init__(self, ssl_context, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

def create_ssl_context(ciphers='HIGH:!DH:!aNULL'):
    '''Create an SSL context with specified ciphers for client authentication.'''
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.set_ciphers(ciphers)
    return context

def download_pdf(url, file_path, session):
    try:
        response = session.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"File đã được tải về: {file_path}")
        else:
            print(f"Không thể tải file từ {url}. HTTP status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")

def setup_session():
    ssl_context = create_ssl_context()
    adapter = SSLAdapter(ssl_context)
    session = requests.Session()
    session.mount('https://', adapter)
    session.headers.update({
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://vpdt.angiang.gov.vn',
        'Referer': 'https://vpdt.angiang.gov.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    })
    return session
