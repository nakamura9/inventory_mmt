import datetime
import pytz

import pandas as pd
from django.core.exceptions import *
import time
from inv import models as inv_models

from common_base.models import Account


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
            pass        
            

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
            pass
    
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


def role_test(user):
    try:
        acc = Account.objects.get(username=user.username)
    except:
        return False
    return acc.role == "admin" 



def parse_spares_file(status_store, file_name):
    fil =  pd.read_csv(file_name)
    file_length = fil.shape[0]
    status_store["messages"].append("Starting...")
    status_store["file_length"] = file_length

    """cols
    warehouse | product | alpha | unit_code | description | supplier | quantity physical | quantity on order | current_cost | min_stock_level 
    """

    i= 0
    while i < file_length:
        try:
            inv_models.Spares(name = fil.iloc[i, 1],
            description = fil.iloc[i, 4],
            stock_id = fil.iloc[i,1],
            quantity = fil.iloc[i, 10],
            last_order_price = fil.iloc[i, 12],
            reorder_quantity = int(fil.iloc[i, 11])).save()
            status_store["successful"] += 1
        except Exception as e:
            status_store["messages"].append(str(e))
            status_store["errors"] += 1
        finally:
            i += 1
    
    status_store["running"] = False
    status_store["finished"] = True
    status_store["messages"].append("Finished processing")
    status_store["stop"] = time.time()

def parse_file(status_store, file_name):
    fil = pd.read_csv(file_name)
    file_length = fil.shape[0]
    status_store["messages"].append("Starting...")
    
    status_store["file_length"] = file_length
    i=0
    while i < file_length:
        try:
            while True:
                try:
                    num = int(fil.iloc[i,0])
                    break
                except:
                    status_store["errors"] += 1
                    status_store["messages"].append("Error: %s row: %d: There is missing data in this row" % (str(fil.iloc[i,0]), i))
                    i += 1
                
            if len(str(num)) % 2 != 0:
                id_string =  "0" + str(num)
            else:
                id_string = str(num)
            
            
            name = str(fil.iloc[i,1])
            name = "".join( [ j if ord(j) < 128 else ' ' for j in name] )
            
            if len(id_string) == 4:
                #Section 
                machine = inv_models.Machine.objects.get(pk=id_string[:2])
                inv_models.Section(unique_id=id_string,
                        section_name=name,
                        machine=machine).save()
                status_store["successful"] += 1
            
            elif len(id_string) == 6:
                #Subt Unit
                machine = inv_models.Machine.objects.get(pk=id_string[:2])
                section = inv_models.Section.objects.get(pk=id_string[:4])
                inv_models.SubUnit(unique_id=id_string,
                        unit_name=name,
                        machine=machine,
                        section=section).save()
                status_store["successful"] += 1

            elif len(id_string) == 8:
                #Sub assembly
                machine = inv_models.Machine.objects.get(pk=id_string[:2])
                section = inv_models.Section.objects.get(pk=id_string[:4])
                subunit = inv_models.SubUnit.objects.get(pk=id_string[:6])
                inv_models.SubAssembly(unique_id=id_string,
                            unit_name=name,
                            machine = machine,
                            section = section,
                            subunit = subunit).save()
                status_store["successful"] += 1

            elif len(id_string) == 10:
                #Component
                machine = inv_models.Machine.objects.get(pk=id_string[:2])
                section = inv_models.Section.objects.get(pk=id_string[:4])
                subunit = inv_models.SubUnit.objects.get(pk=id_string[:6])
                subassy = inv_models.SubAssembly.objects.get(pk=id_string[:8])
                inv_models.Component(unique_id=id_string,
                            component_name=name,
                            machine=machine,
                            section=section,
                            subunit=subunit,
                            subassembly=subassy).save()
                status_store["successful"] += 1

            i = i +  1

        except ObjectDoesNotExist as e:
            status_store["errors"] += 1
            status_store["messages"].append("Error: row %d: %s with id: %s -> %s" % (i, str(e), id_string, name))
            i += 1
        except IOError as e:
            status_store["errors"] += 1
            status_store["messages"].append("Error: row %d: %s" % (i, str(e)))
        
        except IndexError:
            status_store["running"] = False
            status_store["finished"] = True
            status_store["messages"].append("Finished processing")
            status_store["stop"] = time.time()
            break
