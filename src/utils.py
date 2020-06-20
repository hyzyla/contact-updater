import logging

import jinja2
from flask import request

from .models import User

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

AUTH_KEY = 'auth_key'


def get_session():
    token = request.cookies.get(AUTH_KEY)
    if not token:
        logging.info('No auth key in cookies')
        return None

    session = User.get_by_key(token)
    if not session:
        logging.info('Session not exist')
        return None

    logging.info('Session exist {user_id}'.format(user_id=session.user_id))
    return session


def render_template(template, data=None):
    data = data or {}
    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(data)


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }


def create_new_user(user_id, credentials):
    return User(
        user_id=user_id,
        google_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=' '.join(credentials.scopes),
        parent=User.get_parent_key(),
    )
