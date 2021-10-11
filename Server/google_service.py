import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/userinfo.email', 'openid']

def gen_auth_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    authorization_url, state = flow.authorization_url(
        approval_prompt='force',
        access_type='offline',
        include_granted_scopes='true')
    return authorization_url

def code_to_creds_json(state, code):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        state=state)
    flow.redirect_uri = 'http://localhost:5000/oauth2callback'
    flow.fetch_token(code = code)
    return flow.credentials.to_json()

def get_email_from_json_credentials(json_creds):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    return user_info['email']

def add_event_to_google_calendar(json_creds, start_time, end_time, name):
    creds = Credentials.from_authorized_user_info(json_creds, SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    body = {"summary" : name, "start" : {"dateTime": start_time.isoformat()}, "end" : {"dateTime": end_time.isoformat()}}
    service.events().insert(calendarId = "primary", body = body).execute()
