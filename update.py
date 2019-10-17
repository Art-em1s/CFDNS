import requests
import json
import logging
logging.basicConfig(filename='script.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

IP_API = 'https://api.ipify.org?format=json'
CF_API_KEY = '000'
CF_EMAIL = 'example@example.com'

headers = {
    'X-Auth-Email': CF_EMAIL,
    'X-Auth-Key': CF_API_KEY,
    'Content-Type': "application/json",
    }

resp = requests.get(IP_API).json()
ip = resp['ip']

response = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers, params={"status":"active","page":"1","per_page":"20","order":"status","direction":"desc","match":"all"}).json()

for item in response['result']:
    r = requests.get("https://api.cloudflare.com/client/v4/zones/{}/dns_records?type=A".format(item['id']), headers=headers).json()
    if r['success'] == True:
        for record in r['result']:
            if record['content'] == ip:
                continue
            else:
                resp = requests.put(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(item['id'], record['id']),
                    json={
                        'type': 'A',
                        'name': record['name'],
                        'content': ip,
                        'proxied': True
                    },
                    headers=headers)
                assert resp.status_code == 200
                logging.info("Record '{}' updated to {}".format(record['name'], ip))
    else:
        logging.info(r)
