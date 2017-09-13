import requests
import hmac
import hashlib
import base64

PUBLIC_KEY = '##'
PRIVATE_KEY = '##'
URL = 'https://www.poolstat.net.au/restapi/v1/ladders'

digest = hmac.new(PRIVATE_KEY, URL, digestmod=hashlib.sha256).hexdigest()
# signature = base64.b64encode(digest).decode()

print digest
#print signature

headers = {
    'X-Public': PUBLIC_KEY,
    'X-Hash': digest
};

def get_response():
    params = {"year": "2017"}
    return requests.get(URL, headers=headers)

res = get_response()
print res
