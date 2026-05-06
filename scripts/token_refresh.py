import os
import kiteconnect
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('KITE_API_KEY')
API_SECRET = os.getenv('KITE_API_SECRET')

kite = kiteconnect.KiteConnect(api_key=API_KEY)

# Try saved access token
access_token = os.getenv('KITE_ACCESS_TOKEN')
if access_token:
    kite.set_access_token(access_token)
    try:
        kite.profile()
        print('Saved token is valid. No action needed.')
    except Exception:
        print('Token expired. Fresh login required.')
        access_token = None

if not access_token:
    print('Open this URL in your browser.')
    print(kite.login_url())
    request_token = input('Paste request token here: ')
    data = kite.generate_session(request_token=request_token, api_secret=API_SECRET)
    access_token = data['access_token']

    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path, 'r') as f: lines = f.readlines()
    with open(env_path, 'w') as f:
        for line in lines:
            f.write(f'KITE_ACCESS_TOKEN={access_token}\n' if line.startswith('KITE_ACCESS_TOKEN') else line)

    kite.set_access_token(access_token)
    print('Authenticated and token saved.')