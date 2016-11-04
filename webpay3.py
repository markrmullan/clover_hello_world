# https://docs.clover.com/faq/how-do-i-use-the-web-api-to-pay-for-an-order/
# https://docs.clover.com/build/developer-pay-api/
import requests
from Crypto.PublicKey import RSA
from base64 import b64encode

from webpay_secrets import *

merchantID = "SJ925JDCKKTJJ"
orderID = "7NZKPSWGKJ034"

# Getting secrets to encrypt cc info
url = 'https://sandbox.dev.clover.com/v2/merchant/' + merchantID + '/pay/key'
headers = {"Authorization": "Bearer " + API_TOKEN}
response = requests.get(url, headers = headers).json()

# print response

modulus = long(response['modulus'])
exponent = long(response['exponent'])
prefix = long(response['prefix'])

RSAkey = RSA.construct((modulus, exponent))

publickey = RSAkey.publickey()
encrypted = publickey.encrypt(cardNumber, prefix)
cardEncrypted = b64encode(encrypted[0])

# YYBQTK5SVXQ2P
post_data = {
    "orderId": orderID,
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

posturl = 'https://sandbox.dev.clover.com/v2/merchant/' + merchantID + '/pay'
postresponse = requests.post(
    posturl,
    headers = headers,
    data= post_data
    ).json()

print postresponse
