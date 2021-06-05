import datetime


# Useful to convert 
# [date_start(date), time_start(time), time_end(time)] 
# =>
# [start(datetime), end(datetime)]
def to_dt(date, time_start, time_end):
    if not isinstance(date, datetime.date):
        raise TypeError('date({0}) must be date'.format(date.__class__.__name__))
    elif not isinstance(time_start, datetime.time):
        raise TypeError('time({0}) must be date'.format(time_end.__class__.__name__))
    elif not isinstance(time_end, datetime.time):
        raise TypeError('time_end({0}) must be date'.format(time_end.__class__.__name__))
    to_add = datetime.timedelta(days = 1 if time_start >= time_end else 0)
    return {
            'start': datetime.datetime.combine(date, time_start),
            'end': datetime.datetime.combine(date + to_add, time_end)
            }
