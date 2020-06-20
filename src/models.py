from google.cloud import ndb
from google.oauth2.credentials import Credentials


ndb_client = ndb.Client()


class User(ndb.Model):
    token = ndb.StringProperty()
    user_id = ndb.StringProperty()

    contact_id = ndb.StringProperty()

    google_token = ndb.StringProperty()
    refresh_token = ndb.StringProperty()
    token_uri = ndb.StringProperty()
    client_id = ndb.StringProperty()
    client_secret = ndb.StringProperty()
    scopes = ndb.StringProperty()

    date = ndb.DateTimeProperty(auto_now_add=True)
    date_token_refreshed = ndb.DateTimeProperty(auto_now_add=True)
    date_contact_updated = ndb.DateTimeProperty(auto_now_add=True)

    def get_credential_dict(self):
        return {
            'token': self.google_token,
            'refresh_token': self.refresh_token,
            'token_uri': self.token_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scopes': self.scopes.split(' ')
        }

    def get_credentials(self):
        return Credentials(**self.get_credential_dict())

    @staticmethod
    def select_one(query):
        result = query.fetch(1)
        return result[0] if result else None

    @classmethod
    def get_by_key(cls, token):
        query = cls.query(cls.token == token, ancestor=cls.get_parent_key())
        return cls.select_one(query)

    @classmethod
    def get_by_user_id(cls, user_id):
        query = cls.query(cls.user_id == user_id, ancestor=cls.get_parent_key())
        return cls.select_one(query)

    @classmethod
    def get_parent_key(cls):
        return ndb.Key(cls, 'Session')

    @classmethod
    def get_for_update(cls):
        return (
            cls.query(
                cls.token != None,
                ancestor=cls.get_parent_key()
            )
            .fetch()
        )

    @classmethod
    def get_for_token_refresh(cls):
        return (
            cls.query(ancestor=cls.get_parent_key())
            .order(-cls.date_token_refreshed)
            .fetch()
          )
