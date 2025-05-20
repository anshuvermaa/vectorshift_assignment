# slack.py
import json
import secrets
import base64
import hashlib
import asyncio
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import requests
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from config import settings
# Replace these with your HubSpot app details & redirect URL

CLIENT_ID = settings.hubspot_client_id
CLIENT_SECRET = settings.hubspot_client_secret
REDIRECT_URI = settings.hubspot_redirect_uri

AUTHORIZATION_URL = settings.hubspot_authorization_url
TOKEN_URL = settings.hubspot_token_url
scopes = (
    "oauth"
)


async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')

    code_verifier = secrets.token_urlsafe(64)
    m = hashlib.sha256()
    m.update(code_verifier.encode('utf-8'))
    code_challenge = base64.urlsafe_b64encode(m.digest()).decode('utf-8').replace('=', '')

    params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': scopes.strip(),
    'state': encoded_state,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256',
    'response_type': 'code',
}
    auth_url = f'{AUTHORIZATION_URL}?{httpx.QueryParams(params)}&optional_scope=crm.objects.contacts.read'

    await asyncio.gather(
        add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600),
        add_key_value_redis(f'hubspot_verifier:{org_id}:{user_id}', code_verifier, expire=600),
    )
    print(f"Authorization URL: {auth_url}")
    
    return auth_url


async def oauth2callback_hubspot(request: Request):
    print(f"Callback received with query params: {request.query_params}")
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')

    if not code or not encoded_state:
        raise HTTPException(status_code=400, detail='Missing code or state')

    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state, code_verifier = await asyncio.gather(
        get_value_redis(f'hubspot_state:{org_id}:{user_id}'),
        get_value_redis(f'hubspot_verifier:{org_id}:{user_id}'),
    )

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code,
        'code_verifier': code_verifier,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Token exchange failed: {resp.text}")
        tokens = resp.json()

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(tokens), expire=86400)

    await asyncio.gather(
        delete_key_redis(f'hubspot_state:{org_id}:{user_id}'),
        delete_key_redis(f'hubspot_verifier:{org_id}:{user_id}'),
    )

    close_window_script = """
    <html><body><script>window.close();</script></body></html>
    """

    return HTMLResponse(content=close_window_script)


async def get_hubspot_credentials(user_id, org_id):
    print(f"Fetching HubSpot credentials for user_id: {user_id}, org_id: {org_id}")
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)

    return credentials


def create_integration_item_metadata_object(response_json, item_type, parent_id=None, parent_name=None) -> IntegrationItem:
    parent_id = None if parent_id is None else parent_id + '_HubSpot'

    return IntegrationItem(
        id=response_json.get('id', None) + '_' + item_type,
        name=response_json.get('properties', {}).get('firstname', 'Unknown'),
        type=item_type,
        parent_id=parent_id,
        parent_path_or_name=parent_name,
    )


async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    print(f"Access token creds: {credentials}")
    if not access_token:
        raise HTTPException(status_code=400, detail='Missing access token.')
    url = 'https://api.hubapi.com/crm/v3/objects/contacts?limit=10'
    headers = {'Authorization': f'Bearer {access_token}'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 403:
            raise HTTPException(status_code=403, detail='Forbidden: insufficient scope')
        if resp.status_code == 400:
            raise HTTPException(status_code=400, detail='Bad Request: invalid parameters')
        if resp.status_code == 401:
            raise HTTPException(status_code=401, detail='Unauthorized: token expired or invalid')
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f'Failed to fetch contacts: {resp.text}')
        data = resp.json()
    items_metadata = []
    for item in data.get('results', []):
        items_metadata.append(create_integration_item_metadata_object(item, 'Contact'))
    
    print("Items metadata: ", items_metadata)

    return items_metadata
