import requests

def get(url, body={}, headers={}):
    return requests.get(url, data=body, headers=headers)