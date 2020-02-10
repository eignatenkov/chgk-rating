import requests
import json


def api_call(url):
    response = requests.get(url)
    return json.loads(response.content.decode("UTF-8"))