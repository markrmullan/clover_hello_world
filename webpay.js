// https://docs.clover.com/faq/how-do-i-use-the-web-api-to-pay-for-an-order/
// https://docs.clover.com/build/developer-pay-api/
const http = require('http');
const NodeRSA = require('node-rsa');

////////// BEGIN SCRIPT CONFIG SETUP //////////
// merchantID = "SJ925JDCKKTJJ"
const target_env = "api.clover.com"; // or https://sandbox.dev.clover.com/
const path = "/v2/merchant/";
const merchantID = "Q9WPB0CY15SP2";
// orderID = "7NZKPSWGKJ034";
const orderID = "PNQXBTEJKYSFJ";
// API_TOKEN = "7d7a73fb-9de4-f891-2251-7124cbf07df3";
const API_TOKEN = "371c3db2-0547-7abc-793b-2d138584ad14";
const cardNumber = '4761739001010010';
const expMonth = 12;
const expYear = 2018;
const CVV = null;

////////// END SCRIPT CONFIG SETUP //////////

// Getting secrets to encrypt cc info
const url = target_env + merchantID + '/pay/key';
const headers = {"Authorization": "Bearer " + API_TOKEN};
// const response = requests.get(url, headers = headers).json()

const options = {
  host: target_env,
  path: path,
  method: 'GET',
  headers: headers
}

try {
  // http.get(options, callback);
  http.request(options, callback);
} catch (err) {
  console.log(err.message);
}

function callback(response) {
  // const modulus = long(response['modulus']);
  const modulus = response.modulus;
  const exponent = response.exponent;
  const prefix = response.prefix;
  // const exponent = long(response['exponent']);
  // const prefix = long(response['prefix']);

  // console.log(response);

  // const RSAkey = RSA.construct((modulus, exponent));
  const RSAkey = new NodeRSA({modulus: exponent});
  console.log(RSAkey);

  const publickey = RSAkey.publickey;
  const encrypted = publickey.encrypt(cardNumber, prefix);
  const cardEncrypted = b64encode(encrypted[0]);

  const post_data = {
      "orderId": orderID,
      "currency": "usd",
      "amount": 5,
      "expMonth": expMonth,
      "cvv": CVV,
      "expYear": expYear,
      "cardEncrypted": cardEncrypted,
      "last4": cardNumber.slice(-4, -1),
      "first6": cardNumber.slice(0, 6)
  };

  console.log(post_data.last4);
  console.log(post_data.first6);

  const posturl = target_env + merchantID + '/pay';
  const postresponse = requests.post(
      posturl,
      headers = headers,
      data= post_data
      ).json()

  console.log(postresponse.toJson());
}
