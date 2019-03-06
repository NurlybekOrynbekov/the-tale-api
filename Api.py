import uuid
import json
import os

import requests

class Api(object):

    def __init__(self):
        self.session = requests.session()

        self.domain = 'the-tale.org/'
        self.base_url = 'https://' + self.domain

        self.base_params = {
            'api_version': 1.0,
            'api_client': 'test-1.0.0'
        }

        self.application_info = {
            'application_name': 'test_app',
            'application_info': 'testing',
            'application_description': 'testing api'
        }

        self.session.cookies.set('auth', 'not_auth', domain='the-tale.org')

        if(os.path.isfile('session.json')):
            with open('session.json', 'r') as f:
                self.session.cookies.clear()
                requests.utils.add_dict_to_cookiejar(self.session.cookies, json.loads(f.read()))

        self.api_info()

    def save_session(self):
        with open('session.json', 'w') as f:
            d = requests.utils.dict_from_cookiejar(self.session.cookies)
            print(d)
            f.write(json.dumps(d))

    def api_info(self):
        url = 'api/info'
        api_info = self.session.get(self.base_url + url, params=self.base_params)

        csrftoken = api_info.cookies['csrftoken']

        self.session.headers.update({'X-CSRFToken': csrftoken, 'Referer': 'https://the-tale.org/'})

    def auth(self):
        url = 'accounts/third-party/tokens/api/request-authorisation'

        auth_page = self.session.post(self.base_url + url, params=self.base_params, data=self.application_info)

        self.session.cookies.set('auth', 'wait_auth', domain='the-tale.org')

        print(auth_page.text)

    def confirm_auth(self):
        url = 'accounts/third-party/tokens/api/authorisation-state'

        auth_state = self.session.get(self.base_url + url, params=self.base_params)

        data = dict(auth_state.json())

        if data['data']['account_name'] != None:
            self.session.cookies.set('auth', 'auth', domain='the-tale.org')
            self.session.cookies.set('account_id', str(data['data']['account_id']), domain='the-tale.org')

    def account_info(self):
        account_id = self.session.cookies['account_id']
        url = f'accounts/{account_id}/api/show'

        responce = self.session.get(self.base_url + url, params=self.base_params)

        return responce

    def get_auth_state(self):
        return self.session.cookies['auth']

if __name__ == '__main__':
    api = Api()
    # api.api_info()

    if api.get_auth_state() == 'not_auth':
        api.auth()
    elif api.get_auth_state() == 'wait_auth':
        api.confirm_auth()
    elif api.get_auth_state() == 'auth':
        print(json.dumps(api.account_info().json(), sort_keys=True, indent=4))

    api.save_session()