#!/usr/bin/env python
import sys
import requests
import json

url = 'https://devtest.newpage.app/graphql/v1/graphql'
token = ''
try:
  with open('../../token.json') as file:
    data = json.load(file)
    token = data['id_token']
except Exception as e:
  print("Error while reading token.json file", e)
  print("Run npm start at the root of the project in order to generate the token file")
  sys.exit(1)


headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

query = """
query MyQuery {
  carrier {
    id
    label
    createdAt
    updatedAt
  }
}
"""

response = requests.post(url, json={'query': query}, headers=headers)
print(json.dumps(response.json(), indent=2))
