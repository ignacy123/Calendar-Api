from datetime import datetime
import time
import dateutil.tz
import dateutil.parser

rec_dict = {'n' : None, 'd' : "DAILY", 'w' : "WEEKLY", 'm' : "MONTHLY", 'y' : "YEARLY"}

    
def pick_date(hours_minutes = True):
    pattern = '%y/%m/%d %H:%M'
    if not hours_minutes:
        pattern = '%y/%m/%d'
    while(True):
        line = input()
        try:
            date = datetime.strptime(line, pattern)
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
