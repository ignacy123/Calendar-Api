#!/bin/python3
import os.path
import sys
import argparse
import webbrowser
import requests
import json
import dateutil.tz
import dateutil.parser
import time
import picker
from datetime import timedelta
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
    
def get_email():
    token = get_token()
    params = {'token': token}
    try:
        r = requests.get(EMAIL_PATH, params = params)
    except:
        error()
    print(r.json()['email'])
    
def list_all():
    try:
        r = requests.get(LIST_ALL_PATH)
    except:
        error()
    for x in r.json():
        print("{} - {}".format(x[0], x[1]))
    return r.json()

def list_fav():
    token = get_token()
    params = {'token': token}
    try:
        r = requests.get(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 400 and r.content.decode('UTF-8') == 'Wrong token.':
        print("Your token are corrupt (expired or incorrect). Please log in with Google.")
        os.remove('token.json')
        return list_fav()
    for x in r.json():
        print("{} - {}".format(x[0], x[1]))
    return r.json()
    
        
def add_new_fav():
    token = get_token()
    name = get_activity_name(list_all)
    params = {'name' : name, 'token' : token}
    try:
        r = requests.put(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 200:
        print("Successfully added.")
        print(r.json())
    else:
        print(r.json())
    
def del_fav():
    token = get_token()
    name = get_activity_name(list_fav)
    params = {'name' : name, 'token' : token}
    try:
        r = requests.delete(FAV_PATH, params = params)
    except:
        error()
    if r.status_code == 200:
        print("Successfully deleted.")
        print(r.json())
    else: 
        print(r.json())
    
def add_event():
    token = get_token()
    print("Choose start date (yy/mm/dd hh:mm):")
    start_date = picker.pick_date()
    print("Choose end date (yy/mm/dd hh:mm):")
    end_date = picker.pick_date()
    recurrence = picker.pick_recurrence()
    token = get_token()
    name = get_activity_name(list_fav)
    params = {'token' : token, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
    if recurrence:
        params['recurrence'] = recurrence
    try:
        r = requests.put(EVENT_PATH, params = params)
    except:
        error()
    print(r.json())

def list_events():
    token = get_token()
    print("Choose start date (yy/mm/dd):")
    date = picker.pick_date(hours_minutes = False)
    params = {'token' : token, 'date' : date}
    try:
        r = requests.get(EVENT_PATH, params = params)
    except:
        error()
    if r.status_code != 200:
        print(r.json())
        return
    for x in r.json()['activities']:
        event = event_from_list(x)
        actual_start_dates, actual_end_dates = calculate_start_end(date, event['start_date'], event['end_date'], event['recurrence'])
        for x, y in zip(actual_start_dates, actual_end_dates):
            print("{}, start: {}, end: {}, recurrent: {}".format(event['name'], x.strftime("%y/%m/%d %H:%M"), y.strftime("%y/%m/%d %H:%M"), event['recurrence'] if event['recurrence'] else 'No'))
            print()
    
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
            if r.status_code == 400:
                os.remove('token.json')
                print("Invalid token. Please log into the app with Google.")
                obtain_token()
        
def get_token():
    check_token()
    with open('token.json',) as f:
        data = json.load(f)
        return json.dumps(data)

def get_activity_name(f):
    print("Choose activity (number):")
    activities = f()
    while True:
        number = int(input())
        cands = [(x, y) for (x, y) in activities if x == number]
        if(len(cands) > 0): return cands[0][1]
        print("Wrong number. Try again.")
        
def calculate_start_end(date, start_date, end_date, recurrence):
    if not recurrence:
        return [start_date], [end_date]
    #assuming DAILY event is no longer than 24 hours
    elif recurrence == 'DAILY':
        if start_date.date() == end_date.date():
            new_start_date = date.replace(hour = start_date.hour, minute = start_date.minute)
            new_end_date = date.replace(hour = end_date.hour, minute = end_date.minute)
            return [new_start_date], [new_end_date]
        else:
            new_start_date_early = date - timedelta(days = 1)
            new_start_date_early = new_start_date_early.replace(hour = start_date.hour, minute = start_date.minute)
            new_end_date_early = date.replace(hour = end_date.hour, minute = end_date.minute)
            new_start_date_late = date.replace(hour = start_date.hour, minute = start_date.minute)
            new_end_date_late = date + timedelta(days = 1)
            new_end_date_late = new_end_date_late.replace(hour = end_date.hour, minute = end_date.minute)
            return [new_start_date_early, new_start_date_late], [new_end_date_early, new_end_date_late]
    #assuming WEEKLY event is no longer than 7 days
    elif recurrence == 'WEEKLY':
        if start_date.weekday() == end_date.weekday() and (start_date + timedelta(days = 6)) < end_date and start_date.weekday() == date.weekday():
            new_start_date_early = date - timedelta(days = 7)
            new_start_date_early = new_start_date_early.replace(hour = start_date.hour, minute = start_date.minute)
            new_end_date_early = date.replace(hour = end_date.hour, minute = end_date.minute)
            new_start_date_late = date.replace(hour = start_date.hour, minute = start_date.minute)
            new_end_date_late = date + timedelta(days = 7)
            new_end_date_late = new_end_date_late.replace(hour = end_date.hour, minute = end_date.minute)
            return [new_start_date_early, new_start_date_late], [new_end_date_early, new_end_date_late]
        else:
            #to accomodate for rounding error
            delta = date - start_date + timedelta(days = 1)
            amount_of_weeks = delta.days//7
            new_start_date = start_date + timedelta(days = 7*amount_of_weeks)
            new_end_date = end_date + timedelta(days = 7*amount_of_weeks)
            return [new_start_date], [new_end_date]
    #assuming MONTHLY event is no longer than 27 days
    elif recurrence == 'MONTHLY':
        if start_date.day == end_date.day and (start_date + timedelta(days = 27)) < end_date and start_date.day == date.day:
            prev_month = date.month-1 if date.month > 1 else 12
            year_of_prev_month = date.year if date.month > 1 else date.year - 1
            next_month = date.month+1 if date.month < 12 else 1
            year_of_next_month = date.year if date.month < 12 else date.year + 1
            new_start_date_early = start_date.replace(year = year_of_prev_month, month = prev_month)
            new_end_date_early = end_date.replace(year = date.year, month = date.month)
            new_start_date_late = start_date.replace(year = date.year, month = date.month)
            new_end_date_late = end_date.replace(year = year_of_next_month, month = next_month)
            return [new_start_date_early, new_start_date_late], [new_end_date_early, new_end_date_late]
        elif start_date.month < end_date.month and start_date.day <= date.day:
            next_month = date.month+1 if date.month < 12 else 1
            year_of_next_month = date.year if date.month < 12 else date.year + 1
            new_start_date = start_date.replace(year = date.year, month = date.month)
            new_end_date = end_date.replace(year = year_of_next_month, month = next_month)
            return [new_start_date], [new_end_date]
        elif start_date.month < end_date.month and start_date.day > date.day:
            prev_month = date.month-1 if date.month > 1 else 12
            year_of_prev_month = date.year if date.month > 1 else date.year - 1
            new_start_date = start_date.replace(year = year_of_prev_month, month = prev_month)
            new_end_date = end_date.replace(year = date.year, month = date.month)
            return [new_start_date], [new_end_date]
        else:
            new_start_date = start_date.replace(year = date.year, month = date.month)
            new_end_date = end_date.replace(year = date.year, month = date.month)
            return [new_start_date], [new_end_date]
    #assuming YEARLY event is no longer than 1 year
    elif recurrence == 'YEARLY':
        if start_date.month == end_date.month and start_date.day == end_date.day and start_date.year == end_date.year+1 and start_date.month == date.month and start_date.day == date.day:
            new_start_date_early = start_date.replace(year = date.year-1)
            new_end_date_early = end_date.replace(year = date.year)
            new_start_date_late = start_date.replace(year = date.year)
            new_end_date_late = end_date.replace(year = date.year+1)
            return [new_start_date_early, new_start_date_late], [new_end_date_early, new_end_date_late]
        elif start_date.year == end_date.year-1 and (start_date.month < date.month or (start_date.month == date.month and start_date.day <= date.day)):
            new_start_date = start_date.replace(year = date.year)
            new_end_date = end_date.replace(year = date.year+1)
            return [new_start_date], [new_end_date]
        elif start_date.year == end_date.year-1 and (start_date.month > date.month or (start_date.month == date.month and start_date.day > date.day)):
            new_start_date = start_date.replace(year = date.year-1)
            new_end_date = end_date.replace(year = date.year)
            return [new_start_date], [new_end_date]
        else:
            new_start_date = start_date.replace(year = date.year)
            new_end_date = end_date.replace(year = date.year)
            return [new_start_date], [new_end_date]
            
def event_from_list(x):
    event = dict()
    event['name'] = x[0]
    event['start_date'] = dateutil.parser.isoparse(x[1])
    event['end_date'] = dateutil.parser.isoparse(x[2])
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
    elif words[0] == 'le':
        list_events()
    else:
        print_help()
        
    
    
        
