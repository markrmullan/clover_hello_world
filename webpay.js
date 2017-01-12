const http = require('http');

const request = http.request();

///////////////////////////////////////////////////////////////////
//////////////////// BEGIN SCRIPT CONFIG SETUP ////////////////////
///////////////////////////////////////////////////////////////////

const merchantID = "CNKMYYVYGJHXJ"; // sandbox Test Merchant
const target_env = "https://sandbox.dev.clover.com/v2/merchant/";
const orderID = "8GCADRD79S1DW";
const API_TOKEN = "1decda79-717f-8ad5-a3d4-f4f6bb0d7ee0";
const amount = 1000;
const tipAmount = 0;
const taxAmount = 0;
const cardNumber = '4761739001010010';
const expMonth = 12;
const expYear = 2018;
const CVV = null;

/////////////////////////////////////////////////////////////////////
//////////////////// END SCRIPT CONFIG SETUP ////////////////////////
/////////////////////////////////////////////////////////////////////

// GET to /v2/merchant/{mId}/pay/key To get the encryption information needed for the pay endpoint.
let url = target_env + merchantID + '/pay/key'

let options = {
  hostname: 'sandbox.dev.clover.com',
  path: '/v2/merchant/' + merchantID,
  headers: {
    "Authorization": "Bearer " + API_TOKEN
  },
  method: "GET"
};

let req = http.request(options, (res) => {
  console.log(res);
  res.on('data', (chunk) => {
    console.log(chunk);
  });
  res.on('end', () => {
    console.log("no more data in the response");
  })
});

req.on('error', (e) => {
  console.log(e.message);
});

req.end();
//
//
// let
// let response = requests.get(url, headers = headers).json()
//
// modulus = long(response['modulus'])
// exponent = long(response['exponent'])
// prefix = str(response['prefix'])
//
// // construct an RSA public key using the modulus and exponent provided by GET /v2/merchant/{mId}/pay/key
// key = RSA.construct((modulus, exponent))
//
// // create a cipher from the RSA key and use it to encrypt the card number, prepended with the prefix from GET /v2/merchant/{mId}/pay/key
// cipher = PKCS1_OAEP.new(key)
// encrypted = cipher.encrypt(prefix + cardNumber)
//
// // Base64 encode the resulting encrypted data into a string to use as the cardEncrypted' property.
// cardEncrypted = b64encode(encrypted)
//
// post_data = {
//     "orderId": orderID,
//     "currency": "usd",
//     "amount": amount,
//     "tipAmount": tipAmount,
//     "taxAmount": taxAmount,
//     "expMonth": expMonth,
//     "cvv": CVV,
//     "expYear": expYear,
//     "cardEncrypted": cardEncrypted,
//     "last4": cardNumber[-4:],
//     "first6": cardNumber[0:6]
// }
//
// posturl = target_env + merchantID + '/pay'
// postresponse = requests.post(
//     posturl,
//     headers = headers,
//     data= post_data
//     ).json()
//
// print json.dumps(postresponse
