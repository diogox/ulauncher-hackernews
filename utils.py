import datetime

def get_current_time():
    now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)
    return now

def get_time_difference_in_minutes(older, newer):
    days = (newer-older).days
    minutes = days * 24 * 60
    return minutes