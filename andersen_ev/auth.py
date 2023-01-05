import requests
import json

from pycognito import Cognito

from botocore import UNSIGNED
from botocore.config import Config

ANDERSEN_GRAPHQL_PROD     = 'https://graphql.andersen-ev.com'
ANDERSEN_USER_POOL_ID     = 'eu-west-1_t5HV3bFjl'
ANDERSEN_CLIENT_ID        = '23s0olnnniu5472ons0d9uoqt9'
ANDERSEN_USER_POOL_REGION = 'eu-west-1'

"""
# uncomment to enable request logging
import logging
import contextlib
from http.client import HTTPConnection # py3
HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""

class AndersenAuth:
    def __init__(self):
        self.session = requests.Session()
        self.cognito = None

    def _unauth_api(self, uri, body=None):
        headers = { 'Content-Type': 'application/json' }
        r = self.session.post(ANDERSEN_GRAPHQL_PROD+uri, headers=headers, data = json.dumps(body) if body else None)
        return json.loads(r.content)

    def _get_username(self, email):
        r = self._unauth_api('/get-pending-user', {'email':email})
        return r['username']

    def authenticate(self, email, password):
        """ Authenticate with the AndersenEV cloud API
        Args:
            email(str): Email address used to register with the Konnect+ app
            password(str)
        Returns:
            id_token(str): Access token returned by AWS Cognito service 
        """  
        username = self._get_username(email)
        
        cognito = self.cognito = Cognito(
            user_pool_id=ANDERSEN_USER_POOL_ID,
            user_pool_region=ANDERSEN_USER_POOL_REGION,
            client_id=ANDERSEN_CLIENT_ID,
            username=username,
            # signature_version needed for device confirmation
            botocore_config=Config(signature_version=UNSIGNED) 
        )
        
        cognito.authenticate(password)
        return cognito.id_token


