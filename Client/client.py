#!/bin/python3
import sys
import argparse
import webbrowser
import requests

import picker
import datecalc as dc
import googleservice as gs

PATH = "http://localhost:5000"
parser = argparse.ArgumentParser()
parser.add_argument('--path', default=PATH)
args = parser.parse_args()

ACCESS_PATH = args.path+"/access"
gs.ACCESS_PATH = ACCESS_PATH
EMAIL_PATH = args.path+"/email"
gs.EMAIL_PATH = EMAIL_PATH
LIST_ALL_PATH = args.path+"/all"
FAV_PATH = args.path+"/fav"
EVENT_PATH = args.path+"/event"

def get_email():
    token = gs.get_token()
    params = {'token': token}
    try:
        r = requests.get(EMAIL_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    print(r.json()['email'])
    
def list_all():
    try:
        r = requests.get(LIST_ALL_PATH)
    except:
        error()
    activities = r.json()['activities']
    for x in activities:
        print("{} - {}".format(x[0], x[1]))
    return activities

def list_fav():
    token = gs.get_token()
    params = {'token': token}
    try:
        r = requests.get(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    activities = r.json()['activities']
    for x in activities:
        print("{} - {}".format(x[0], x[1]))
    return activities
    
        
def add_new_fav():
    token = gs.get_token()
    try:
        name = get_activity_name(list_all)
    except:
        print("Cancelled.")
        return
    params = {'name' : name, 'token' : token}
    try:
        r = requests.put(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    if r.status_code == 200:
        print("Successfully added.")
        print(r.json())
    else:
        print(r.json())
    
def del_fav():
    token = gs.get_token()
    try:
        name = get_activity_name(list_fav)
    except:
        print("Cancelled.")
        return
    params = {'name' : name, 'token' : token}
    try:
        r = requests.delete(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    if r.status_code == 200:
        print("Successfully deleted.")
    print(r.json())
    
def add_event():
    token = gs.get_token()
    print("Choose start date (yy/mm/dd hh:mm):")
    start_date = picker.pick_date()
    print("Choose end date (yy/mm/dd hh:mm):")
    end_date = picker.pick_date()
    recurrence = picker.pick_recurrence()
    try:
        name = get_activity_name(list_fav)
    except:
        print("Cancelled.")
        return
    params = {'token' : token, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
    if recurrence:
        params['recurrence'] = recurrence
    try:
        r = requests.put(EVENT_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    print(r.json())

def list_events():
    token = gs.get_token()
    print("Choose start date (yy/mm/dd):")
    date = picker.pick_date(hours_minutes = False)
    params = {'token' : token, 'date' : date}
    try:
        r = requests.get(EVENT_PATH, params = params)
    except:
        error()
    if r.status_code == 401:
        print("Corrupt token.")
        os.remove('token.json')
        return
    if r.status_code != 200:
        print(r.json())
        return
    events = r.json()['activities']
    if len(events) == 0:
        print("No events on this day.")
        return
    for x in events:
        event = event_from_list(x)
        actual_start_dates, actual_end_dates = dc.calculate_start_end(date, event['start_date'], event['end_date'], event['recurrence'])
        for x, y in zip(actual_start_dates, actual_end_dates):
            print("{}, start: {}, end: {}, recurrent: {}".format(event['name'], dc.format_date(x), dc.format_date(y), event['recurrence'] if event['recurrence'] else 'No'))
            print()
    
def get_activity_name(f):
    print("Choose activity (number):")
    print("Press enter to abandon.")
    activities = f()
    while True:
        number = int(input())
        cands = [(x, y) for (x, y) in activities if x == number]
        if(len(cands) > 0): return cands[0][1]
        print("Wrong number. Try again.")

def event_from_list(x):
    event = dict()
    event['name'] = x[0]
    event['start_date'] = dc.parse_date(x[1])
    event['end_date'] = dc.parse_date(x[2])
    event['recurrence'] = x[3]
    return event
    
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
    print("le - list events for a given day")
    print("exit - exit")

gs.check_token()
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
    elif words[0] == 'le':
        list_events()
    elif words[0] == 'exit':
        sys.exit(0)
    else:
        print_help()
