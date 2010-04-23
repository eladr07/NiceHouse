from datetime import datetime

def current_month():
    now = datetime.now()
    if now.day <= 22:
        now = datetime(now.month == 1 and now.year - 1 or now.year, 
                       now.month == 1 and 12 or now.month - 1, 
                       now.day)
    return now