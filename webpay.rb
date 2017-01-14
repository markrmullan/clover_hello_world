require 'open-uri'
require 'byebug'
require 'json'

###############################################
########## BEGIN SCRIPT CONFIG SETUP ##########
###############################################

merchantID = "CNKMYYVYGJHXJ" # sandbox Test Merchant
target_env = "https://sandbox.dev.clover.com/v2/merchant/"
orderID = "8GCADRD79S1DW"
api_token = "1decda79-717f-8ad5-a3d4-f4f6bb0d7ee0"
amount = 1000
tipAmount = 0
taxAmount = 0
cardNumber = '4761739001010010'
expMonth = 12
expYear = 2018
cvv = nil

 # 'https://sandbox.dev.clover.com/v2/merchant/CNKMYYVYGJHXJ/pay/key'

###############################################
########## END SCRIPT CONFIG SETUP ############
###############################################

# GET to /v2/merchant/{mId}/pay/key To get the encryption information needed for the pay endpoint.

# TODO: put this in a try catch
response = JSON.parse(open(target_env + merchantID + '/pay/key',
"Authorization" => "Bearer #{api_token}").read)

modulus = response["modulus"].to_i
exponent = response["exponent"].to_i
prefix = response["prefix"]
