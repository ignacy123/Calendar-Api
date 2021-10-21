import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import tzlocal
import pkgutil
import json

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

def gen_auth_url():
    secret_data = pkgutil.get_data(__package__, 'client_secret.json').decode()
    secret_dict = json.loads(secret_data)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        secret_dict,
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    authorization_url, state = flow.authorization_url(
        approval_prompt='force',
        access_type='offline',
        include_granted_scopes='true')
    return authorization_url

def code_to_creds_json(state, code):
    secret_data = pkgutil.get_data(__package__, 'client_secret.json').decode()
    secret_dict = json.loads(secret_data)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        secret_dict,
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    flow.fetch_token(code = code)
    return json.loads(flow.credentials.to_json())

#assumes there's 'token' and 'refresh_token' in the dict
def token_to_creds_json(token_dict):
    if 'token' not in token_dict.keys() or 'refresh_token' not in token_dict.keys():
        raise InvalidTokenException("Missing token or refresh_token.")
    secret_data = pkgutil.get_data(__package__, 'client_secret.json').decode()
    secret_dict = json.loads(secret_data)['web']
    creds_json = {'token' : token_dict['token'], 'refresh_token' : token_dict['refresh_token'], 'token_uri' : secret_dict['token_uri'], 'client_id' : secret_dict['client_id'], 'client_secret' : secret_dict['client_secret'], 'scopes' : SCOPES}
    return creds_json
    
def get_email_from_json_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info['email']

def token_to_creds_json_and_email(token_dict):
    creds_json = token_to_creds_json(token_dict)
    email = get_email_from_json_credentials(creds_json)
    return creds_json, email

def add_event_to_google_calendar(json_creds, start_time, end_time, name, recurrence):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    body = None
    if recurrence:
        start_time = start_time.replace(tzinfo = None)
        end_time = end_time.replace(tzinfo = None)
        body = {"summary" : name, "start" : {"timeZone": str(tzlocal.get_localzone()), "dateTime": start_time.isoformat()}, "end" : {"timeZone": str(tzlocal.get_localzone()), "dateTime": end_time.isoformat()}, 
                "recurrence" : ['RRULE:FREQ={}'.format(recurrence)]}
    else:
        body = {"summary" : name, "start" : {"timeZone": str(tzlocal.get_localzone()), "dateTime": start_time.isoformat()}, "end" : {"timeZone": str(tzlocal.get_localzone()), "dateTime": end_time.isoformat()}}
    print(body)
    service.events().insert(calendarId = "primary", body = body).execute()
    
class InvalidTokenException(Exception):
    """Invalid token has been sent in the args."""
