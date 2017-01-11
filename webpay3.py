# https://docs.clover.com/faq/how-do-i-use-the-web-api-to-pay-for-an-order/
# https://docs.clover.com/build/developer-pay-api/
from Crypto.Cipher import PKCS1_OAEP
import requests
from Crypto.PublicKey import RSA
from base64 import b64encode
import json

########## BEGIN SCRIPT CONFIG SETUP ##########
merchantID = "CNKMYYVYGJHXJ" # sandbox Test Merchant
# merchantID = "B4DKP7TRRQHA0" # EU Prod test merchant
target_env = "https://sandbox.dev.clover.com/v2/merchant/" # or https://sandbox.dev.clover.com/v2/merchant/
orderID = "8GCADRD79S1DW"
# orderID = "3DJ9RGWSZ9B3A" # test for EU prod order
API_TOKEN = "1decda79-717f-8ad5-a3d4-f4f6bb0d7ee0" # for Sandbox Test Merchant
# API_TOKEN = "cbcce4c4-74ec-767b-c34a-7a3def936c78" # for EU prod account
amount = 1000
tipAmount = 0
taxAmount = 0
cardNumber = '4761739001010010'
expMonth = 12
expYear = 2018
CVV = None

########## END SCRIPT CONFIG SETUP ##########

# Getting secrets to encrypt cc info
url = target_env + merchantID + '/pay/key'
headers = {"Authorization": "Bearer " + API_TOKEN}
response = requests.get(url, headers = headers).json()

modulus = long(response['modulus'])
exponent = long(response['exponent'])
prefix = str(response['prefix'])

# construct an RSA public key using the modulus and exponent provided by GET /v2/merchant/{mId}/pay/key
key = RSA.construct((modulus, exponent))

# create a cipher from the RSA key and use it to encrypt the card number, prepended with the prefix from GET /v2/merchant/{mId}/pay/key
cipher = PKCS1_OAEP.new(key)
encrypted = cipher.encrypt(prefix + cardNumber)

# Base64 encode the resulting encrypted data into a string which you will send to Clover in the “cardEncrypted” field.
cardEncrypted = b64encode(encrypted)

post_data = {
    "orderId": orderID,
    "currency": "usd",
    "amount": amount,
    "tipAmount": tipAmount,
    "taxAmount": taxAmount,
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
