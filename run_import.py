import requests

i = 0
with open('log2.txt') as f:
    for line in f:
        i += 1
        first_comma = line.index(',')
        second_comma = line.index(',', first_comma + 1)
        third_comma = line.index(',', second_comma + 1)
        timestamp = line[:first_comma]
        print(timestamp)
        url = line[first_comma+1:second_comma]
        ip = line[second_comma+1:third_comma]
        agent = line[third_comma+1:]

        res = requests.post('http://127.0.0.1:5000/api/v1/traffic', json={
            'url': url,
            'ip_addr': ip,
            'user_agent': agent,
            'timestamp': timestamp
        }, headers={'Authorization': 'x123456'})
        print(res)
