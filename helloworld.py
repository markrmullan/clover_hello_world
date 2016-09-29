import os
import cgi
import datetime
import urllib
import wsgiref.handlers
import webapp2
import pdb
import logging
import urllib2
from urlparse import urlparse
# from urllib import urlparse
import urlparse
import json

from webapp2 import WSGIApplication, Route

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

from secret_settings import *

access_token_str = '0'
# merchant_id = 'ZXWVDF5S051T2'
# app_id = 'E0SVKZCX95KXE' also aliased as client_id that is a query param to
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
            global access_token_str
            print "have a code!"

            response = urllib2.urlopen("https://www.clover.com/oauth/token?client_id=E0SVKZCX95KXE&client_secret=" + CLIENT_SECRET + "&code=" + code)
            html = response.read()
            access_token_str = str(json.loads(html)[u'access_token'])
            print "ACCESS TOKEN IS:", access_token_str
            response.close()

            request = urllib2.Request("https://api.clover.com/v3/merchants/ZXWVDF5S051T2/", None, {"Authorization": "Bearer cce6bda8-4844-c126-b956-b0ceedd63519"})
            rest_api_response = urllib2.urlopen(request)
            rest_api_html = rest_api_response.read()
            rest_api_json = json.loads(rest_api_html)
            rest_api_response.close()

            address_request = urllib2.Request(rest_api_json[u'address']['href'], None, {"Authorization": "Bearer cce6bda8-4844-c126-b956-b0ceedd63519"})
            address_file = urllib2.urlopen(address_request)
            address = address_file.read()
            address_file.close()

            email_request = urllib2.Request(rest_api_json[u'owner']['href'], None, {"Authorization": "Bearer cce6bda8-4844-c126-b956-b0ceedd63519"})
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

class Callback(webapp2.RequestHandler):
    def get(self):
        print "oauth callback printing!!!!"

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

class CreateUser(webapp2.RequestHandler):
    def get(self):

        # data = self.request.get('data').replace("'", '"')
        data = self.request.get('data').replace('false', "False")
        data = eval(data)

        address = eval(data['address'])
        email = eval(data['email'])
        # email = eval(data.get('email'))
        print "data object is:", data
        # print "email object is:", email

        # print "DATA OBJECT RETURNED IS:", data
        # data = json.loads(data)
        # print data[0]
        # data = json.loads(data.replace("'", '"'))

        # print data[0]
        # print data.address



        if data:
            # json_data = json.loads(data)


            template_values = {
                "address1": address.get('address1'),
                "address2": address.get("address2"),
                "email": email.get("email")
            }

            path = os.path.join(os.path.dirname(__file__), 'sign_up.html')
            self.response.out.write(template.render(path, template_values))

# ROUTES
routes = [
    Route (r'/', handler = MainPage),
    Route (r'/sign', handler = Guestbook),
    Route (r'/callback', handler = Callback),
    Route (r'/users/new', handler = CreateUser)
]

app = webapp2.WSGIApplication(routes, debug=True)

def main():
    app.run()

if __name__ == "__main__":
    main()
