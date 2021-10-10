#!/bin/python3
import os.path
import sys
import argparse
import webbrowser
import requests
import json

PATH = "http://localhost:5000"
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
args = parser.parse_args()

ACCESS_PATH = args.path+"/access"
EMAIL_PATH = args.path+"/email"
LIST_ALL_PATH = args.path+"/lall"
FAV_PATH = args.path+"/fav"

def error():
    print("Server down, aborting.")
    sys.exit(-1)
    
def get_email():
    creds = get_credentials()
    params = {'credentials': creds}
    try:
        r = requests.get(EMAIL_PATH, params = params)
    except:
        error()
    print(r.content.decode('UTF-8'))
    
def list_all():
    try:
        r = requests.get(LIST_ALL_PATH)
    except:
        error()
    for x in r.json():
        print("{} - {}".format(x[0], x[1]))
    return r.json()

def list_fav():
    creds = get_credentials()
    params = {'credentials': creds}
    try:
        r = requests.get(FAV_PATH, params = params)
    except:
        error()
    for x in r.json():
        print("{} - {}".format(x[0], x[1]))
    return r.json()
    
        
def add_new_fav():
    creds = get_credentials()
    print("Choose activity to add (number):")
    activities = list_all()
    number = int(input())
    name = [(x, y) for (x, y) in activities if x == number][0][1]
    params = {'name' : name, 'credentials' : creds}
    try:
        r = requests.put(FAV_PATH, params = params)
    except:
        error()
    print(r.json())
    
def del_fav():
    creds = get_credentials()
    print("Choose activity to delete (number):")
    activities = list_fav()
    number = int(input())
    name = [(x, y) for (x, y) in activities if x == number][0][1]
    params = {'name' : name, 'credentials' : creds}
    try:
        r = requests.delete(FAV_PATH, params = params)
    except:
        error()
    print(r.json())
    

def obtain_token():
    try:
        r = requests.get(ACCESS_PATH)
    except:
        error()
    if r.status_code != 200:
        error()
    access_url = r.json()['url']
    webbrowser.open(access_url)
    with open('token.json', 'w') as token_file:
        while True:
            line = input()
            token_file.write(line)
            if line == '}':
                break
            
def check_token():
    if not os.path.exists('token.json'):
        print("Currently you are not logged in. Please log into the app with Google.")
        print("Paste the credentials here:")
        obtain_token()
        
def get_credentials():
    check_token()
    with open('token.json',) as f:
        data = json.load(f)
        return json.dumps(data)

def print_help():
    print("Available commands:")
    print("help - help")
    print("email - your email")
    print("lall - list all available activities")
    print("lfav - list all favourite activities")
    print("afav - add a new favourite activity")
    print("dfav - delete a favourite activity")

check_token()
for line in sys.stdin:
    if line=='\n': continue
    words = line.split()
    if words[0] == 'help' || len(words)>1:
        print_help()
    elif words[0] == 'email':
        get_email()
    elif words[0] == 'lall':
        list_all()
    elif words[0] == 'lfav':
        list_fav()
    elif words[0] == 'afav':
        add_new_fav()
    elif words[0] == 'dfav':
        del_fav()
    else:
        print_help()
        
    
    
        
