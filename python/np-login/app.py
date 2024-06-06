import asyncio
from math import log
import os
from pydoc import cli
import typing
import requests
import hashlib
import base64
import json
import webbrowser
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from oauthlib.oauth2 import WebApplicationClient
from rich import print, print_json

# Configuration for Azure AD B2C
TENANT_NAME = 'octavenouvellepage'
CLIENT_ID = 'fe829ac8-2ee6-4b24-8538-f14dc54225d3'
POLICY_NAME = 'B2C_1A_SIGNUP_SIGNIN'
REDIRECT_URI = 'http://localhost:4567/callback'
SCOPE = 'openid profile offline_access'
DISCOVERY_URL = f'https://{TENANT_NAME}.b2clogin.com/{TENANT_NAME}.onmicrosoft.com/{POLICY_NAME}/v2.0/.well-known/openid-configuration'

# Allow HTTP for OAuthlib
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Generate the code verifier and challenge
def generate_code_verifier_and_challenge():
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('utf-8')
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge

code_verifier, code_challenge = generate_code_verifier_and_challenge()

# Create the FastAPI app
app = FastAPI()
client = WebApplicationClient(CLIENT_ID)

# Fetch discovery document
discovery_doc = requests.get(DISCOVERY_URL).json()
authorization_endpoint = discovery_doc['authorization_endpoint']
token_endpoint = discovery_doc['token_endpoint']

@app.get('/callback', response_class=HTMLResponse)
async def callback(request: Request):

    query_dict = client.parse_request_uri_response(  # noqa
        uri=str(request.url), 
    )
    if "error" in query_dict:
        return query_dict


    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=str(request.url),
        redirect_url=REDIRECT_URI,
        code=query_dict['code'],
        code_verifier=code_verifier
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=None
    )

    asyncio.create_task(print_token(token_response.json()))
    return 'Login successful! You can close this window.'


async def print_token(token_response: typing.Mapping[str, typing.Any]):
    print("Token response:")
    print_json(json.dumps(token_response))
    await asyncio.sleep(1)
    print("Ending program...")
    global server
    server.should_exit = True
    await server.shutdown()

@app.get('/', response_class=HTMLResponse)
async def index():
    return 'Nothing here'

auth_url = None
server = None

if __name__ == '__main__':
    auth_url, *_ = client.prepare_authorization_request(
        authorization_endpoint,
        redirect_url=REDIRECT_URI,
        scope=SCOPE,
        code_challenge=code_challenge,
        code_challenge_method='S256'
    )
    print("Open the following URL in your browser:")
    print(auth_url)
    webbrowser.open(auth_url)
    import uvicorn
    config = uvicorn.Config(app=app, host='0.0.0.0', port=4567, log_level='warning')
    server = uvicorn.Server(config)
    try:
        server.run()
    except:
        pass
