# https://docs.clover.com/faq/how-do-i-use-the-web-api-to-pay-for-an-order/
# https://docs.clover.com/build/developer-pay-api/
import requests
from Crypto.PublicKey import RSA
from base64 import b64encode
import json

########## BEGIN SCRIPT CONFIG SETUP ##########
# merchantID = "SJ925JDCKKTJJ"
target_env = "https://api.clover.com/v2/merchant/" # or https://sandbox.dev.clover.com/v2/merchant/
merchantID = "Q9WPB0CY15SP2"
# orderID = "7NZKPSWGKJ034"
orderID = "PNQXBTEJKYSFJ"
# API_TOKEN = "7d7a73fb-9de4-f891-2251-7124cbf07df3"
API_TOKEN = "371c3db2-0547-7abc-793b-2d138584ad14"
cardNumber = '4761739001010010'
expMonth = 12
expYear = 2018
CVV = None

########## END SCRIPT CONFIG SETUP ##########

# Getting secrets to encrypt cc info
url = target_env + merchantID + '/pay/key'
headers = {"Authorization": "Bearer " + API_TOKEN}
response = requests.get(url, headers = headers).json()

print response

modulus = long(response['modulus'])
exponent = long(response['exponent'])
prefix = long(response['prefix'])

RSAkey = RSA.construct((modulus, exponent))

publickey = RSAkey.publickey()
encrypted = publickey.encrypt(cardNumber, prefix)
cardEncrypted = b64encode(encrypted[0])

post_data = {
    "orderId": orderID,
    "currency": "usd",
    "amount": 5,
    "expMonth": expMonth,
    "cvv": CVV,
    "expYear": expYear,
    "cardEncrypted": cardEncrypted,
    "last4": cardNumber[-4:],
    "first6": cardNumber[0:6]
}

posturl = target_env + merchantID + '/pay'
postresponse = requests.post(
    posturl,
    headers = headers,
    data= post_data
    ).json()

print json.dumps(postresponse)
