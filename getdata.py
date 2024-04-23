from requests import Session, RequestException
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import ssl
import json
from utilities import setup_session

# Initialize session with custom settings
session = setup_session()

# Function to make requests
def make_request(method, url, params=None, data=None):
    try:
        response = session.request(method, url, params=params, data=data)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Request error: {e}")
        return None

# Generic function to fetch data
def fetch_data(token, ma_don_vi, method, url, params=None, data=None):
    if method.lower() == 'get':
        params = params if params else {}
        params.update({'token': token})
    elif method.lower() == 'post':
        data = data if data else {}
        data.update({'token': token})

    return make_request(method, url, params=params, data=data)

def main():
    token = '8423494c9f5965bd44905b027a75f706'
    ma_don_vi = '0'
    
    # Fetch loai van ban
    # url_loai_van_ban = 'https://angiang-api.vnptioffice.vn/api/danh-muc/danh-sach-loai-van-ban-no-authen'
    # response_loai_van_ban = fetch_data(token, ma_don_vi, 'get', url_loai_van_ban)

    # Fetch co quan
    # url_co_quan = 'https://angiang-api.vnptioffice.vn/api/can-bo/ds-dv-by-chuoi-loai-don-vi'
    # response_co_quan = fetch_data(token, ma_don_vi, 'get', url_co_quan)

    # # Fetch van ban di
    url_van_ban_di = 'https://angiang-api.vnptioffice.vn/api/van-ban-di/ds-vb-cong-khai-an-giang'
    data_van_ban_di = {
        'den_ngay': '21/02/2024',
        'ma_don_vi': '1088',
        'nam': '2024',
        'page': '1',
        'size': '20',
        'token': '8423494c9f5965bd44905b027a75f706',
        'tu_khoa': 'số',
        'tu_ngay': '21/01/2024',
    }
    response_van_ban_di = fetch_data(token, '0', 'post', url_van_ban_di, data=data_van_ban_di)

    # Process the responses as needed
    # print("Loai Van Ban:", json.dumps(response_loai_van_ban, indent=4, ensure_ascii=False))
    # print("Co Quan:", json.dumps(response_co_quan, indent=4, ensure_ascii=False))
    print("Van Ban Di:", json.dumps(response_van_ban_di, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
