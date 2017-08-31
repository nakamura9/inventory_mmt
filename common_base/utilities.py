import datetime
import pytz

def time_choices(start, stop, interval, delta=False):
    """
    start and stop are strings that represent time in the format H:M:00.
    interval is the time to be incremented between start and stop in the
    same format as above.
    The function returns a list of tuples in human readable format from
    the start time up to but not including the end time. 
    The function can either return strings that correspond to time or 
    strings that correspond to timedelta objects.
    """

    times = []
    try:
        _start = datetime.datetime.strptime(start, "%H:%M:%S").time()
        _stop = datetime.datetime.strptime(stop, "%H:%M:%S").time()
        _interval = datetime.datetime.strptime(interval, "%H:%M:%S").time()
    except:
        raise Exception("the times supplied do not match the required format")

    current_time = _start
    while current_time < _stop:
        if delta:
            times.append((datetime.timedelta(hours=current_time.hour,
                                            minutes=current_time.minute),
                                                current_time.strftime("%H:%M")))
        else:
            times.append((current_time ,current_time.strftime("%H:%M")))
        
        current_time = (datetime.datetime.combine(datetime.date.today(), current_time) \
                        + datetime.timedelta(hours = _interval.hour,
                                            minutes=_interval.minute,
                                            seconds=_interval.second)).time()
    return times


def filter_by_dates(queryset, start, stop):
    date_format = "%m/%d/%Y"
    if start:
        start = datetime.datetime.strptime(start, date_format)
        start = pytz.timezone("Africa/Harare").localize(start)
        try:
            queryset = queryset.filter(creation_date__gte = start)
        except:
            queryset = queryset.filter(creation_epoch__gte = start)
    if stop:
        stop = datetime.datetime.strptime(stop, date_format)
        stop = pytz.timezone("Africa/Harare").localize(stop)
        try:
            queryset = queryset.filter(creation_date__lte = stop)
        except:
            queryset = queryset.filter(creation_epoch__lte = stop)
    return queryset