import requests

params = {'url': '/', 'ip_addr': '127.0.0.1', 'user_agent': 'Firefox'}
r = requests.post('http://127.0.0.1:5001/report_traffic', params=params)