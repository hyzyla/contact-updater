import json

import webapp2
from google.appengine.api import users
from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = '109522712080-go60mkcqu0h0bbm0kgp90i2pjiic6vtv.apps.googleusercontent.com'
def get_request_json(request):
    return json.loads(request.body)


class MainHandler(webapp2.RequestHandler):

    def get(self):

        self.response.write('Hello, webapp2!')


class LoginHandler(webapp2.RedirectHandler):

    def post(self):
        data = get_request_json(self.request)
        token = data[u'token']

        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']
            print userid

        except ValueError:
            # Invalid token
            pass


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/login', LoginHandler)
], debug=True)
