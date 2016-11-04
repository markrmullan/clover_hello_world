# https://docs.clover.com/faq/how-do-i-use-the-web-api-to-pay-for-an-order/
# https://docs.clover.com/build/developer-pay-api/
import os

# from google.appengine.api import apiproxy_stub_map
# from google.appengine.api import urlfetch_stub
#
# apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
# apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())

# from google.appengine.api import urlfetch
from Crypto.PublicKey import RSA
from base64 import b64encode
import requests

# CC info
cardNumber = '4761739001010010'
expMonth = 12
expYear = 2018
CVV = 5444444

# Getting secrets to encrypt cc info
url = 'https://sandbox.dev.clover.com/v2/merchant/SJ925JDCKKTJJ/pay/key'
headers = {"Authorization": "Bearer 3a440b6b-a76f-bdb3-f999-2a3d2c1a63ee"}
response = requests.get(url, headers = headers).json()

print response

modulus = long(response['modulus'])
exponent = long(response['exponent'])
prefix = long(response['prefix'])

RSAkey = RSA.construct((modulus, exponent))

publickey = RSAkey.publickey()
encrypted = publickey.encrypt(cardNumber, prefix)
cardEncrypted = b64encode(encrypted[0])

# YYBQTK5SVXQ2P

post_data = {
    "orderId": "7NZKPSWGKJ034",
    "currency": "usd",
    "amount": 5,
    # "token":"8Z1C6RPH2A2CM",
    # "authCode":"561740",
    "expMonth": expMonth,
    "cvv": CVV,
    "expYear": expYear,
    "cardEncrypted": cardEncrypted,
    "last4": cardNumber[-4:],
    "first6": cardNumber[0:6]
}

posturl = 'https://sandbox.dev.clover.com/v2/merchant/SJ925JDCKKTJJ/pay'
postresponse = requests.post(
    posturl,
    headers = headers,
    # method='POST',
    data= post_data
    ).json()



print postresponse
