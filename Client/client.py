#!/bin/python3
import os.path
import sys
import argparse
import webbrowser
import requests
import json
import dateutil.tz
import time
from datetime import datetime

PATH = "http://localhost:5000"
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
args = parser.parse_args()

ACCESS_PATH = args.path+"/access"
EMAIL_PATH = args.path+"/email"
LIST_ALL_PATH = args.path+"/lall"
FAV_PATH = args.path+"/fav"
EVENT_PATH = args.path+"/event"
rec_dict = {'n' : None, 'd' : "DAILY", 'w' : "WEEKLY", 'm' : "MONTHLY", 'y' : "YEARLY"}
    
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
    if r.status_code == 400 and r.content.decode('UTF-8') == 'Wrong credentials.':
        print("Your credentials are corrupt (expired or incorrect). Please log in with Google.")
        os.remove('token.json')
        return list_fav()
    for x in r.json():
        print("{} - {}".format(x[0], x[1]))
    return r.json()
    
        
def add_new_fav():
    creds = get_credentials()
    name = get_activity_name(list_all)
    params = {'name' : name, 'credentials' : creds}
    try:
        r = requests.put(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 200:
        print("Successfully added.")
    else:
        print("Something went wrong, try again.")
    
def del_fav():
    creds = get_credentials()
    name = get_activity_name(list_fav)
    params = {'name' : name, 'credentials' : creds}
    try:
        r = requests.delete(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 200:
        print("Successfully deleted.")
    else: 
        print("Something went wrong, try again.")
    
def add_event():
    creds = get_credentials()
    print("Choose start date (yy/mm/dd hh:mm):")
    start_date = pick_date()
    print("Choose end date (yy/mm/dd hh:mm):")
    end_date = pick_date()
    recurrence = pick_recurrence()
    creds = get_credentials()
    name = get_activity_name(list_fav)
    params = {'credentials' : creds, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
    if recurrence:
        params['recurrence'] = recurrence
    try:
        r = requests.put(EVENT_PATH, params = params)
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
            if line.endswith('}'):
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
    
def pick_date():
    while(True):
        line = input()
        try:
            date = datetime.strptime(line, '%y/%m/%d %H:%M')
            date = date.replace(tzinfo = dateutil.tz.tzoffset(None, time.localtime().tm_gmtoff))
            return date
        except:
            print("Sorry, but this isn't quite right. Try again.")
            
def pick_recurrence():
    while True:
        print("Recurrent?\n n - No \n d - Daily \n w - weekly \n m - monthly \n y - yearly")
        line = input()
        if line in ['n', 'd', 'w', 'm', 'y']:
            rec = rec_dict[line]
            return rec
        print("Sorry, try again.")

def get_activity_name(f):
    print("Choose activity (number):")
    activities = f()
    while True:
        number = int(input())
        cands = [(x, y) for (x, y) in activities if x == number]
        if(len(cands) > 0): return cands[0][1]
        print("Wrong number. Try again.")
    
def error():
    print("Server down, aborting.")
    sys.exit(-1)

def print_help():
    print("Available commands:")
    print("help - help")
    print("email - your email")
    print("lall - list all available activities")
    print("lfav - list all favourite activities")
    print("afav - add a new favourite activity")
    print("dfav - delete a favourite activity")
    print("ae - add a new event to the calendar")

check_token()
for line in sys.stdin:
    if line=='\n': continue
    words = line.split()
    if words[0] == 'help' or len(words)>1:
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
    elif words[0] == 'ae':
        add_event()
    else:
        print_help()
        
    
    
        
