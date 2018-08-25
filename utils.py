import datetime

def get_current_time():
    now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)
    return now

def get_time_difference_in_minutes(older, newer):
    seconds = (newer-older).seconds
    minutes = seconds / 60.0
    return minutes

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]