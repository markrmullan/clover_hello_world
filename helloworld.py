import os
import cgi
import datetime
import urllib
import wsgiref.handlers
import webapp2
import pdb
import logging
import urllib2
import json

from webapp2 import WSGIApplication, Route

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

access_token_str = '0'
merchant_id = 'ZXWVDF5S051T2'

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
            global merchant_id
            print "have a code!"

            response = urllib2.urlopen("https://www.clover.com/oauth/token?client_id=E0SVKZCX95KXE&client_secret=daecf720-c7f8-0684-1e1d-23d926ba2e9e&code=" + code)
            html = response.read()
            access_token_str = str(json.loads(html)[u'access_token'])
            print "ACCESS TOKEN IS:", access_token_str
            response.close()

            rest_api_response = urllib2.urlopen("https://api.clover.com/v3/merchants/ZXWVDF5S051T2/orders?access_token=cce6bda8-4844-c126-b956-b0ceedd63519")
            rest_api_html = rest_api_response.read()
            print "TEST REST API STRING IS", rest_api_html

            self.redirect('http://localhost:8080/callback')
        else:
            print "no code here"
            self.redirect('http://www.clover.com/oauth/authorize?client_id=E0SVKZCX95KXE&redirect_uri=http://localhost:8080/callback')

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

        # access_token = self.request.get('access_token')
        # print "access token is:", access_token

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

        # response = requests.get("https://www.clover.com/v3/merchants/ZXWVDF5S051T2/employees/3A7A0Y9BZ7MEA")
        # owner = response.owner
        # self.response.out.write("this page is owned by", owner)

        # owner = urllib2.urlopen(https://www.clover.com/v3/merchants/ZXWVDF5S051T2/employees/3A7A0Y9BZ7MEA).read()
        # self.response.out.write("this page is owned by", owner)


# ROUTES
routes = [
    Route (r'/', handler = MainPage),
    Route (r'/sign', handler = Guestbook),
    Route (r'/callback', handler = Callback)
]

app = webapp2.WSGIApplication(routes, debug=True)

def main():
    app.run()

if __name__ == "__main__":
    main()
