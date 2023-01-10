import requests
import json

from . import auth

ANDERSEN_MOBILE_PROD  = 'https://mobile.andersen-ev.com'
ANDERSEN_MOBILE_STAGE = 'https://mobile-staging.andersen-ev.com'

class AndersenMobile:

    def __init__(self, id_token = None):
        self.session = requests.Session()
        self.id_token = id_token

    def authenticate(self, email, password):
        aa = auth.AndersenAuth()
        self.id_token = aa.authenticate(email, password)

    def _api(self, uri, body=None):
        assert self.id_token, "User has not been authenticated"

        headers = {
          "Content-Type": "application/json",
          'Authorization': f'Bearer {self.id_token}'
        }
        
        r = self.session.get(
            ANDERSEN_MOBILE_PROD+uri, 
            headers=headers, 
            data = json.dumps(body) if body else None
        )
        #data = dump.dump_all(r)
        #print(data.decode('utf-8'))
        return json.loads(r.content)

    def register_mobile_device(self, device):
        pass

    def get_devices(self):
        return self._api('/api/getDevices')
