import requests
import json
webhook_url = 'https://5316-2405-201-8016-8826-e806-1b2c-83e7-7de7.ngrok-free.app/webhook'
data = { 'name': 'This is an example for webhook' }
requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})