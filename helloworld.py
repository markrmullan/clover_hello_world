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

access_token_str = ''
global_code = ''
# merchant_id = 'ZXWVDF5S051T2'
# app_id = 'E0SVKZCX95KXE' also aliased as cl\ient_id that is a query param to
# API TOKEN cce6bda8-4844-c126-b956-b0ceedd63519
# https://www.clover.com/oauth/authorize


class Greeting(db.Model):
    # Models an individual Guestbook entry with an author, content and date.
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

def guestbook_key(guestbook_name=None):
    # Constructs a datastore key for a Guestbook entity with guestbook_name
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
    def get(self):
        code = self.request.get('code')
        if code:
            global_code = code
            global access_token_str

            url = "https://www.clover.com/oauth/token?client_id=E0SVKZCX95KXE&client_secret=" + CLIENT_SECRET + "&code=" + code
            try:
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    access_token_str = str(json.loads(result.content)[u'access_token'])
                else:
                    self.response.status_code = result.status_code
            except:
                logging.exception('Caught exception fetching url')

            request = urllib2.Request("https://api.clover.com/v3/merchants/ZXWVDF5S051T2/", None, {"Authorization": "Bearer " + access_token_str})
            rest_api_response = urllib2.urlopen(request)
            rest_api_html = rest_api_response.read()
            rest_api_json = json.loads(rest_api_html)
            rest_api_response.close()

            address_request = urllib2.Request(rest_api_json[u'address']['href'], None, {"Authorization": "Bearer " + access_token_str})
            address_file = urllib2.urlopen(address_request)
            address = address_file.read()
            address_file.close()

            email_request = urllib2.Request(rest_api_json[u'owner']['href'], None, {"Authorization": "Bearer " + access_token_str})
            email_file = urllib2.urlopen(email_request)
            email = email_file.read()
            email_file.close()

            ############################################################
            ### OBJECT TO USE FOR PARSING, AUTOCOMPLETING FORMS, ETC ###
            ############################################################
            self.redirect('http://localhost:8080/users/new?' + urllib.urlencode({'data': {
                                                                                          'address': address,
                                                                                          'email': email
                                                                                          }
                                                                                  }))
        else:
            # No code, redirect to Clover OAuth
            self.redirect('http://www.clover.com/oauth/authorize?client_id=E0SVKZCX95KXE&redirect_uri=http://localhost:8080')

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

class NewUserForm(webapp2.RequestHandler):
    def get(self):
        data = self.request.get('data').replace('false', "False").replace('true', "True")
        # clover server responds back with 'true' or 'false' strings
        # python will throw an error for uncapitalized booleans, so we convert
        if len(data) > 0:
            data = eval(data)
            address = eval(data['address'])
            email = eval(data['email'])

            template_values = {
                "email": email.get("email"),
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
        template_values = {}

        path = os.path.join(os.path.dirname(__file__), 'new_order.html')
        self.response.out.write(template.render(path, template_values))

class CreateUser(webapp2.RequestHandler):
    def post(self):
        # simulate loading screen, in live app, would actually create a User
        # and store in db.

        print "Creating user in db, loading..."
        time.sleep(2)
        self.redirect("http://localhost:8080/orders/new")

class CreateOrder(webapp2.RequestHandler):
    def post(self):
        params = urlparse.parse_qs(self.request.body)
        global access_token_str
        global global_code

        # response = urllib2.urlopen("https://www.clover.com/oauth/token?client_id=E0SVKZCX95KXE&client_secret=" + CLIENT_SECRET + "&code=" + global_code)
        # html = response.read()
        # access_token_str = str(json.loads(html)[u'access_token'])
        # response.close()

        print access_token_str
        print access_token_str
        print access_token_str
        print access_token_str
        print access_token_str
        print access_token_str


        # order_request = urllib2.Request('https://www.clover.com/v3/merchants/ZXWVDF5S051T2/orders',
        #                                 json.loads(json.dumps({
        #                                     "note": params["note"][0],
        #                                     "total": params["total"][0],
        #                                     "client_id": "E0SVKZCX95KXE",
        #                                     "client_secret": CLIENT_SECRET,
        #                                     "code": global_code
        #                                 })),
        #                                 {"Authorization": "Bearer " + access_token_str}
        #                                 )
        # order_response = urllib2.urlopen(order_request)


# ROUTES
routes = [
    Route (r'/', handler = MainPage),
    Route (r'/sign', handler = Guestbook),
    Route (r'/guestbook/index', handler = GuestbookIndex),
    Route (r'/users/new', handler = NewUserForm),
    Route (r'/users/create', handler = CreateUser),
    Route (r'/orders/new', handler = NewOrderForm),
    Route (r'/orders/create', handler = CreateOrder)
]

app = webapp2.WSGIApplication(routes, debug=True)

def main():
    app.run()

if __name__ == "__main__":
    main()
