import logging
import os
from uuid import uuid4

import google_auth_oauthlib.flow
from flask import Flask, redirect, request, url_for

from src.services import db_context
from . import services
from .models import User
from .utils import AUTH_KEY, create_new_user, get_session, render_template


flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=[
        'https://www.googleapis.com/auth/contacts',
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ],
    redirect_uri=os.getenv('REDIRECT_URL'),
)
flow.code_verifier = 'OgHKlh1C9CnbBND77iiMQGH8xo89d5qTLqPJHYyBidcaSO5zBI'

app = Flask(__name__)


@app.route('/auth', methods=['GET'])
@db_context
def auth():
    logging.info('Log in by new user')

    code = request.args.get('code')
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user = services.get_user_profile(credentials)
    user_id = user[u'resourceName']

    # Try to select user from database
    user = User.get_by_user_id(user_id)
    if not user:
        user = create_new_user(user_id, credentials)
        contact = services.find_contact(credentials)

        # Create new contact with name Test Contact
        if not contact:
            logging.info('Contact not found create new one')
            contact = services.create_create(credentials)

        user.contact_id = contact[u'resourceName']

    # Update refresh token if necessary
    if credentials.refresh_token and user.refresh_token != credentials.refresh_token:
        logging.info('New refresh token provided')
        user.refresh_token = credentials.refresh_token

    auth_key = str(uuid4())
    user.token = auth_key
    user.put()

    response = redirect('/')
    response.set_cookie(AUTH_KEY, auth_key)
    return response


@app.route('/login', methods=['GET'])
@db_context
def login():
    consent_prompt = int(request.args.get('consent', 0))
    extra = {}
    if consent_prompt:
        # Request new refresh token
        extra['prompt'] = 'consent'

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        **extra
    )
    logging.info('Redirect to {}'.format(str(authorization_url)))
    return redirect(str(authorization_url))


@app.route('/logout', methods=['GET'])
@db_context
def logout():
    session = get_session()
    if session:
        # Just remove token from database,
        # for preventing losing refresh and token data
        session.token = None
        session.put()

    response = redirect(url_for('login'))
    response.delete_cookie(AUTH_KEY)
    return response


@app.route('/', methods=['GET'])
@db_context
def index():
    session = get_session()

    if not session:
        logging.info('Redirect to /login')
        return redirect(url_for('login'))

    credentials = session.get_credentials()
    contact = services.get_contact_by_id(session.contact_id, credentials)

    return render_template(
        template='index.jinja2',
        data={
            'user_id': session.user_id,
            'contact': contact,
        }
    )


@app.route('/update', methods=['GET'])
@db_context
def update():
    logging.info('Cron job for updating contact is started')
    for user in User.get_for_update():
        logging.info('Updating contact {0}'.format(user.contact_id))

        credentials = user.get_credentials()
        contact = services.get_contact_by_id(user.contact_id, credentials)
        if contact:
            etag = contact[u'etag']
            services.update_contact(user.contact_id, etag, credentials)

            logging.info('Contact {0} was updated'.format(user.contact_id))
        else:
            logging.warning('Contact {0} not exist'.format(user.contact_id))

    return 'OK'
