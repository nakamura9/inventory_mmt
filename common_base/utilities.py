import datetime
import pytz


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