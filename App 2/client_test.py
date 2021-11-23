import requests
import json
import sseclient

channel = 'channel'
header = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    }

user = 'Thiago'

response = requests.get('http://10.0.0.109:5000/users', params={'channel': channel, 'user': user, 'request': 'visit'}, headers=header, stream=True).json()
print(response)

print(requests.post('http://10.0.0.109:5000/users', data={'user': user,
                                                         'enquete': 'Bonde de Floripa',
                                                         'local': 'Florianopolis',
                                                         'limite': '2021-11-20',
                                                         'votos': "['2021-11-19','2021-11-20','2021-11-21']"}))

response = 'http://10.0.0.109:5000/event'
client = sseclient.SSEClient(response)
print("-------------")
for event in client:
    print(event.data)