from datetime import datetime
from functools import wraps

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models import ndb_client


def get_people_service(credentials):
    return build(
        'people',
        version='v1',
        credentials=credentials,
        cache_discovery=False,
    ).people()


def find_contact(credentials):
    connections = get_people_service(credentials).connections()

    request = connections.list(
        resourceName='people/me',
        pageSize=2000,
        personFields='names',
    )
    while request is not None:
        response = request.execute()
        for contact in response.get('connections', []):
            names = contact.get(u'names', [])
            if not names:
                continue
            given_name = names[0].get(u'givenName', u'')

            if given_name.lower() == 'test contact':
                return contact

        request = connections.list_next(previous_request=request,
                                        previous_response=response)

    return None


def create_create(credentials):
    return (
        get_people_service(credentials)
        .createContact(body={'names': [{'givenName': 'Test Contact'}]})
        .execute()
    )


def get_user_profile(credentials):
    return get_contact_by_id('people/me', credentials)


def update_contact(contact_id, etag, credentials):
    return (
        get_people_service(credentials)
        .updateContact(
            resourceName=contact_id,
            body={
                "etag": etag,
                "biographies": [
                    {
                        "value": datetime.now().strftime('%m/%d/%Y %I:%M %p')
                    }
                ],
            },
            updatePersonFields='biographies',
        )
        .execute()
    )


def not_found_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 404:
                return None
            raise e

    return wrapper


@not_found_exception
def get_contact_by_id(contact_id, credentials):
    return (
        get_people_service(credentials)
        .get(resourceName=contact_id, personFields='names,addresses,biographies')
        .execute()
    )


def db_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ndb_client.context():
            return func(*args, **kwargs)
    return wrapper
