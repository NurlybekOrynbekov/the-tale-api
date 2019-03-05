import requests
import pickle
import os

base_url = 'https://the-tale.org/'
base_params = {
    'api_version': 1.0,
    'api_client': 'test-1.0.0'
}

session = requests.session()
data = {}

if os.path.isfile('session'):
    with open('session', 'rb') as f:
        session.cookies.update(pickle.load(f))
        print(session.cookies)
else:
    session.cookies.set('auth', 'not_auth', domain='the-tale.org')

def auth():
    auth_data = {
        'application_name': 'test_app',
        'application_info': 'testing',
        'application_description': 'testing api'
    }
    auth_url = 'accounts/third-party/tokens/api/request-authorisation'

    auth_page = session.post(os.path.join(base_url, auth_url), params=base_params, data=auth_data)

    print(auth_page.text)

    session.cookies.set('auth', 'wait_auth', domain='the-tale.org')

def confirm_auth():
    auth_state_url = 'accounts/third-party/tokens/api/authorisation-state'

    auth_state = session.get(os.path.join(base_url, auth_state_url), params=base_params)
    
    data = dict(auth_state.json())

    print(data)

    if data['data']['account_name'] != None:
        session.cookies.set('auth', 'auth', domain='the-tale.org')
        data['account_id'] = data['data']['account_id']

def account_info():
    account_id = data['account_id']
    url = f'accounts/{account_id}/api/show'

    responce = session.get(os.path.join(base_url, url), params=base_params)

    return responce



api_info = session.get(os.path.join(base_url, 'api/info'), params=base_params)

csrftoken = api_info.cookies['csrftoken']

session.headers.update({'X-CSRFToken': csrftoken, 'Referer': 'https://the-tale.org/'})

if(session.cookies['auth'] == 'not_auth'):
    auth()

if(session.cookies['auth'] == 'wait_auth'):
    confirm_auth()

if(session.cookies['auth'] == 'auth'):
    print('authorized')
    player_info = account_info()

    print

with open('session', 'wb') as f:
    pickle.dump(session.cookies, f)