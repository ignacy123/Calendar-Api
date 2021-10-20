import dateutil.tz
import dateutil.parser
import time

from datetime import timedelta
from datetime import datetime

def calculate_start_end(date, start_date, end_date, recurrence):
    if not recurrence:
        return [start_date], [end_date]
    #assuming DAILY event is no longer than 24 hours
    elif recurrence == 'DAILY':
        return calculate_start_end_daily(date, start_date, end_date)
    #assuming WEEKLY event is no longer than 7 days
    elif recurrence == 'WEEKLY':
        return calculate_start_end_weekly(date, start_date, end_date)
    #assuming MONTHLY event is no longer than 27 days
    elif recurrence == 'MONTHLY':
        return calculate_start_end_monthly(date, start_date, end_date)
    #assuming YEARLY event is no longer than 1 year
    elif recurrence == 'YEARLY':
        return calculate_start_end_yearly(date, start_date, end_date)
        
        
def calculate_start_end_daily(date, start_date, end_date):
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
        if start_date.date() != date.date():
            return [new_start_date_early, new_start_date_late], [new_end_date_early, new_end_date_late]
        return [new_start_date_late], [new_end_date_late]
        
        
def calculate_start_end_weekly(date, start_date, end_date):
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
    
def calculate_start_end_monthly(date, start_date, end_date):
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
    
def calculate_start_end_yearly(date, start_date, end_date):
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
    
def parse_date(date):
    return dateutil.parser.isoparse(date)
    
def format_date(date):
    return date.strftime("%y/%m/%d %H:%M")
