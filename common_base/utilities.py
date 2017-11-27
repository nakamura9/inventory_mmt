import datetime
import pytz

def time_choices(start, stop, interval, delta=False):
    """
    Creates a list of times between start and stop separated by interval.

    Inputs
    =======
        start and stop are strings that represent time in the format H:M:00.
        interval is the time to be incremented between start and stop in the
        same format as above.
        delta, boolean, whether return elements are timedeltas
    Returns:
    =======
    The function returns a list of tuples in human readable format from
    the start time up to but not including the end time. 
    either 
        [(timedelta, string), ...]
    or
        [(time, string), ...] 
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
    """Used to filter a queryset between two dates.
    
    Input
    =======
    Queryset
    Start - string (%m/%d/%Y)
    Stop - string (%m/%d/%Y)

    Output
    ========
    Queryset(filtered)

    The filter process involves first first conveting the datetime to a format the django orm understands, pytz.timezone and then filtering accordingly."""

    date_format = "%m/%d/%Y"
    sample = queryset.first()

    if start:
        start = datetime.datetime.strptime(start, date_format)
        start = pytz.timezone("Africa/Harare").localize(start)
        if 'creation_date' in dir(sample):
            queryset = queryset.filter(creation_date__gte= start)
        elif 'creation_epoch' in dir(sample):
            queryset = queryset.filter(creation_epoch__gte = start)
        elif 'execution_date' in dir(sample):
            queryset = queryset.filter(execution_date__gte = start)
        elif 'scheduled_for' in dir(sample):
            queryset = queryset.filter(scheduled_for__gte = start)
        else:
            print "not found"        
            

    if stop:
        stop = datetime.datetime.strptime(stop, date_format)
        stop = pytz.timezone("Africa/Harare").localize(stop)
        if 'creation_date' in dir(sample):
            queryset = queryset.filter(creation_date__lte= stop)
        elif 'creation_epoch' in dir(sample):
            queryset = queryset.filter(creation_epoch__lte = stop)
        elif 'execution_date' in dir(sample):
            queryset = queryset.filter(execution_date__lte = stop)
        elif 'scheduled_for' in dir(sample):
            queryset = queryset.filter(scheduled_for__lte = stop)
        else:
            print "not found"
    
    return queryset


def ajax_required(ret_unexcepted):
    """
    Decorator for determing whether the request is Ajax, in Django-views.

    e.g. in views.py
    
    @ajax_requirxed(HttpResponseBadRequest())
    def index(request):
        pass
    """

    def _ajax_required(func):
        def wrapper(request, *args, **kwargs):
            if not request.is_ajax():
                return ret_unexcepted
            return func(request, *args, **kwargs)
        return wrapper

    return _ajax_required