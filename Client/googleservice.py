import os.path
import json
import requests
import sys
import argparse
import webbrowser

    
def error():
    print("Server down, aborting.")
    sys.exit(-1)

def obtain_token():
    try:
        r = requests.get(ACCESS_PATH)
    except:
        error()
    if r.status_code != 200:
        error()
    print("Paste the token here:")
    access_url = r.json()['url']
    webbrowser.open(access_url)
    with open('token.json', 'w') as token_file:
        while True:
            line = input()
            token_file.write(line)
            if line.endswith('}'):
                break
            
def check_token():
    if not os.path.exists('token.json'):
        print("Currently you are not logged in. Please log into the app with Google.")
        obtain_token()
        return
    else:
        with open('token.json',) as f:
            try:
                token = json.dumps(json.load(f))
            except:
                print("Invalid token. Please log into the app with Google.")
                obtain_token()
                return
            params = {'token' : token}
            try:
                r = requests.get(EMAIL_PATH, params = params)
            except:
                error()
            if r.status_code == 401:
                os.remove('token.json')
                print("Invalid token. Please log into the app with Google.")
                obtain_token()
        
def get_token():
    check_token()
    with open('token.json',) as f:
        data = json.load(f)
        return json.dumps(data) 
