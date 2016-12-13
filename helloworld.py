import os
import cgi
import datetime
import urllib
import wsgiref.handlers
import webapp2
import pdb
import logging
import urllib2
import time
import json
import urlparse

from webapp2 import WSGIApplication, Route

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch

from secret_settings import *

access_token = None
client_id = None
merchant_id = None

class Home(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'home.html')
        self.response.out.write(template.render(path, {}))

class MainPage(webapp2.RequestHandler):
    def get(self):
        global client_id
        global merchant_id
        # retrieve query params from URL
        code = self.request.get('code')
        client_id = self.request.get('client_id')
        merchant_id = self.request.get('merchant_id')

        if code:
            # if there's a code query param, use it to get an access_token by making a request to...
            # https://sandbox.dev.clover.com/oauth/token?client_id=%%%&client_secret=%%%&code=code
            global access_token

            url = "https://sandbox.dev.clover.com/oauth/token?client_id=" + client_id + "&client_secret=" + CLIENT_SECRET + "&code=" + code
            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    # parse access_token from the response body.
                    access_token = str(json.loads(result.content)[u'access_token'])
                else:
                    self.response.status_code = result.status_code
            except:
                logging.exception('Caught exception fetching url')

            # now use this access token to access the REST API and retrieve
            # merchant information we would be interested in

            # example REST API call:

            # In this example, I'll retrieve merchant address and email.
            # Both might be useful for pre-populating my Sign Up form,
            # providing the merchant with a positive signup experience.
            url = "https://sandbox.dev.clover.com/v3/merchants/" + merchant_id + '?expand=owner,address'
            headers = {"Authorization": "Bearer " + access_token}
            result = urlfetch.fetch(
                url = url,
                headers = headers
            )

            # the response from the Clover server is a JSON String.
            # parse the email and address from the Clover response
            email = str(json.loads(result.content)[u'owner'][u'email'])
            address = str(json.loads(result.content)[u'address'])

            # base64 encode the email and address
            query = urllib.urlencode({'data': { 'address': address, 'email': email }})

            # then pass that object as a query param to the Sign Up form.
            self.redirect('http://localhost:8080/users/new?' + query)
        else:
            # If there's no 'code' query param, redirect to begin Clover OAuth.
            # In production, change to https://www.clover.com/oauth/authorize
            self.redirect('https://sandbox.dev.clover.com/oauth/authorize')

class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

class GuestbookIndex(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class Order(db.Model):
    # Models an Order -- set up Webhooks to create these Orders when a Clover order is created
    total = db.IntegerProperty()
    note = db.StringProperty(multiline = False)
    state = db.StringProperty(multiline = False)

class NewUserForm(webapp2.RequestHandler):
    def get(self):
        data = self.request.get('data').replace('false', "False").replace('true', "True")
        # clover server responds back with 'true' or 'false' strings
        # python will throw an error for uncapitalized booleans, so we convert
        if len(data) > 0:
            data = eval(data)
            address = eval(data['address'])
            email = str(data['email'])

            template_values = {
                "email": email,
                "address1": address.get('address1'),
                "address2": address.get("address2"),
                "city": address.get("city"),
                "state": address.get("state"),
                "zip": address.get("zip")
            }

            path = os.path.join(os.path.dirname(__file__), 'sign_up.html')
            self.response.out.write(template.render(path, template_values))
        else:
            print "something went wrong!"
            # TODO: error handling here

class NewOrderForm(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'new_order.html')
        self.response.out.write(template.render(path, {}))

class CreateUser(webapp2.RequestHandler):
    def post(self):
        # simulate loading screen, in live app, would actually create a User
        # and store in db.

        print "Creating user in db, loading..."
        self.redirect("http://localhost:8080/inventory/new")

class RemoveOrder(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'delete_order.html')
        self.response.out.write(template.render(path, {}))

    def post(self):
        global merchant_id
        global access_token

        order_id = urlparse.parse_qs(self.request.body)['id'][0]
        url = "https://sandbox.dev.clover.com/v3/merchants/" + merchant_id + "/orders/" + order_id
        headers = {"Authorization": "Bearer " + access_token, 'Content-Type': 'application/json'}

        try:
            result = urlfetch.fetch(
                url = url,
                method = urlfetch.DELETE,
                headers = headers
            )

            template_values = {
                "order_id": order_id
            }

            path = os.path.join(os.path.dirname(__file__), 'new_order.html')
            self.response.out.write(template.render(path, template_values))
        except:
            logging.exception('error while deleting order')

class NewInventoryForm(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'new_inventory.html')
        self.response.out.write(template.render(path, {}))

class CreateInventoryItem(webapp2.RequestHandler):
    def post(self):
        global merchant_id
        global client_id
        global access_token
        form_data = urlparse.parse_qs(self.request.body)

        url = "https://sandbox.dev.clover.com/v3/merchants/" + merchant_id + "/items"
        headers = {"Authorization": "Bearer " + access_token, 'Content-Type': 'application/json'}

        post_data = json.dumps({
            "name": form_data["name"][0],
            "price": form_data["price"][0],
            "sku": form_data["sku"][0],
            "client_id": client_id,
            "client_secret": CLIENT_SECRET,
        })

        result = urlfetch.fetch(
            url = url,
            method = urlfetch.POST,
            payload = post_data,
            headers = headers)

        result = json.loads(result.content)

        template_values = {
            'name': result[u'name'],
            'price': result[u'price'],
            'sku': result[u'sku'],
            'id': result[u'id']
        }

        path = os.path.join(os.path.dirname(__file__), 'item_created.html')
        self.response.out.write(template.render(path, template_values))

class CreateOrder(webapp2.RequestHandler):
    def post(self):
        global merchant_id
        global client_id
        global access_token
        form_data = urlparse.parse_qs(self.request.body)

        url = "https://sandbox.dev.clover.com/v3/merchants/" + merchant_id + "/orders"
        headers = {"Authorization": "Bearer " + access_token, 'Content-Type': 'application/json'}

        post_data = json.dumps({
            "note": form_data["note"][0],
            "total": form_data["total"][0],
            "client_id": client_id,
            "client_secret": CLIENT_SECRET,
            "state": "open"
        })

        result = urlfetch.fetch(
            url = url,
            method = urlfetch.POST,
            payload = post_data,
            headers = headers)

        result = json.loads(result.content)
        template_values = {
            'note': result[u'note'],
            'currency': result[u'currency'],
            'id': result[u'id'],
            'total': result[u'total']
        }

        path = os.path.join(os.path.dirname(__file__), 'order_created.html')
        self.response.out.write(template.render(path, template_values))

# ROUTES
routes = [
    Route (r'/', handler = MainPage),
    Route (r'/sign', handler = Guestbook),
    Route (r'/guestbook/index', handler = GuestbookIndex),
    Route (r'/users/new', handler = NewUserForm),
    Route (r'/users/create', handler = CreateUser),
    Route (r'/orders/new', handler = NewOrderForm),
    Route (r'/orders/create', handler = CreateOrder),
    Route (r'/orders/remove', handler = RemoveOrder),
    Route (r'/inventory/new', handler = NewInventoryForm),
    Route (r'/inventory/create', handler = CreateInventoryItem),
    Route (r'/home', handler = Home)
]

app = webapp2.WSGIApplication(routes, debug=True)

def main():
    app.run()

if __name__ == "__main__":
    main()
