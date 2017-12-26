# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import threading
import time
import os

from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.core import serializers
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.db.models import Q

from common_base.models import Category, Account
from common_base.utilities import ajax_required, parse_file, parse_spares_file, CSV_RUNNING
from inv import models as inv_models
from inv.forms import RunDataForm
from jobcards.models import SparesRequest
from inventory_mmt import settings


CSV_FILE_STATUS = {"messages":[],
                    "successful": 0,
                    "errors": 0,
                    "start": 0.0,
                    "stop": 0.0,
                    "running": False,
                    "finished": False,
                    "file_length": 0,
                    }
"""The views that correspond to the URLS """


def get_users(request):
    """ajax response used to create a list of users for a form
    
    method: GET
    returns: users -> a list of 2 element lists consisting of pks and 
                        usernames"""

    data = {"users": [[u.pk, u.username] for u in Account.objects.all()]}
    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def update_section(request):
    """Takes json from request and returns the list of sections under the provided machine.
    
    Input: JSON -> "machine": string
    Output: HttpResponse JSON -> "sections": 2 dimensional array
    """

    if request.POST.get("machine", None) == None:
        return Http404()
    
    machine =inv_models.Machine.objects.get(pk= \
                        request.POST["machine"])
    sections = [[section[0], section[1]] for section in machine.section_set.values_list()]
    return HttpResponse(json.dumps(
            {"sections": sections}),
                content_type="application/json")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def update_subunit(request):
    """Takes json from request and returns the list of subunits under the provided section.
    
    Input: JSON -> "section": string
    Output: HttpResponse JSON -> "units": 2 dimensional array
    """
    
    if request.POST.get("section", None) == None:
        return Http404()
    
    section =inv_models.Section.objects.get(pk= \
                        request.POST["section"])
    units = [[unit[0],unit[1]] for unit in section.subunit_set.values_list()]
    return HttpResponse(json.dumps(
            {"units": units}),
                content_type="application/json")


@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def update_subassembly(request):
    """Takes json from request and returns the list of subunits under the provided section.
    
    Input: JSON -> "section": string
    Output: HttpResponse JSON -> "units": 2 dimensional array
    """

    if request.POST.get("unit", None) ==None:
        return Http404()
    
    subunit =inv_models.SubUnit.objects.get(
                    pk= request.POST["unit"])
    
    subassemblies= [[assy[0], assy[1]] for assy in subunit.subassembly_set.values_list()]
    return HttpResponse(json.dumps(
            {"subassemblies": subassemblies}),
                content_type="application/json")


@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def update_components(request):
    """Takes json from request and returns the list of components under the provided subassembly.
    
    Input: JSON -> "subassy": string
    Output: HttpResponse JSON -> "components": 2 dimensional array
    """

    if request.POST.get("subassy", None) == None:
        return Http404()
    
    subassy =inv_models.SubAssembly.objects.get(
                    pk= request.POST["subassy"])
    
    components= [[comp[0],comp[1]] for comp in subassy.component_set.values_list()]
    return HttpResponse(json.dumps(
            {"components": components}),
                content_type="application/json")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def ajaxAuthenticate(request):
    """Authenticates users quickly in username/password combo

    Input: JSON -> "username": string, "password": string
    Output: HTTPResponse JSON-> "authenticated": Boolean
    """
    if authenticate(username=request.POST["username"], 
            password=request.POST["password"]):
        return HttpResponse(json.dumps({"authenticated":True}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({"authenticated":False}),
                            content_type="application/json")

def add_run_data(request):
    """Adds run data to a specific machine.
    
    Done in terms of days hours start date and specific work days
    #will need to add an end date"""
    data = RunDataForm(request.POST)
    print data.errors
    run = data.save()
    inv_models.Machine.objects.get(pk=request.POST["machine"]).run_data.add(run)
    
    return HttpResponse(json.dumps({"success":True}), content_type="application/json")

@csrf_exempt
def add_equipment(request):
    """can return a serialized version of an abitrary inventory item
    
    Input:
    ========
    POST data
        pk, type

    Output
    =========
    JSON
    """

    models = {"machine": inv_models.Machine,
            "section": inv_models.Section,
            "subunit": inv_models.SubUnit,
            "subassembly": inv_models.SubAssembly,
            "component": inv_models.Component}
    pk = request.POST.get("pk")
    model_type = request.POST.get("type")
    equipment = [models[model_type].objects.get(pk=pk)]
    
    data = serializers.serialize("json", equipment)
    return HttpResponse(data, content_type="application/json")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def get_combos(request):
    """
    Used along with other functions to provide information used to populate
    search input datalists

    method: POST
    =============
    Input : 
    =============
        str -> search string
        model -> the models to be searched

    Output: 
    =============
        matches -> a list of matching data corresponding to the search string
    """

    s = request.POST.get("str", None)
    _model = request.POST.get("model", None)

    
    if s and _model:
        mapping = {"account":get_account,
        "machine":get_machine,
        "section":get_section,
        "subunit":get_subunit,
        "subassembly":get_subassy,
        "component":get_component,
        "spares":get_spares,
        "inv":inv_list}
        
        items = mapping[_model](s)
        
        #return the first 20 results for really long queries
        if len(items) > 20:
            items = items[:20]
            
        return HttpResponse(json.dumps({"matches":items}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"matches": []}))

def inv_list(s):
    #two steps back 
    items = [[c.pk, c.component_name, c.machine.machine_name, 0] for c in \
                inv_models.Component.objects.filter(
                    Q(component_name__startswith=s) |
                    Q(unique_id__startswith=s))]
    items += [[sa.pk, sa.unit_name, sa.machine, 2] for sa in \
                inv_models.SubAssembly.objects.filter(
                    Q(unit_name__startswith=s) |
                    Q(unique_id__startswith=s))]
    return items


def get_machine(name):
    return [m.machine_name for m in inv_models.Machine.objects.filter(
        Q(machine_name__startswith=name) |
        Q(unique_id__startswith=name))]


def get_section(name):
    return [s.section_name for s in inv_models.Section.objects.filter(
        Q(section_name__startswith=name) |
        Q(unique_id__startswith=name))]


def get_subunit(name):
    return [s.unit_name for s in inv_models.SubUnit.objects.filter(
        Q(unit_name__startswith=name) |
        Q(unique_id__startswith=name))]


def get_subassy(name):
    """Searches subassemblies by name"""
    return [s.unit_name for s in inv_models.SubAssembly.objects.filter(
        Q(unit_name__startswith=name) |
        Q(unique_id__startswith=name))]


def get_component(name):
    """Searches a component by name, and id"""
    return [c.component_name for c in inv_models.Component.objects.filter(
            Q(component_name__startswith=name) |
            Q(unique_id__startswith=name))]


def get_spares(name):
    """searches spares by name and stock_id """
    return [s.stock_id for s in inv_models.Spares.objects.filter(
            Q(stock_id__startswith=name) | 
            Q(name__startswith=name))]


def get_account(name):
    """Searches accounts by username, first name and last name"""
    return [a.username for a in Account.objects.filter(
                                Q(username__startswith=name) |
                                Q(first_name__startswith=name) |
                                Q(last_name__startswith=name))]


def add_category(request):
    """Quick addition of categories to the database."""
    if request.method == "POST":
        data = request.POST.copy().dict()
        data.pop("csrfmiddlewaretoken")
        Category(**data).save()
        return HttpResponse("0")


def spares_request(request):
    sr = SparesRequest(unit=request.POST["unit"],
                    quantity=request.POST["quantity"])
    if request.POST["name"] != "":
        sr.name = request.POST["name"]
    else:
        sr.linked_spares = inv_models.Spares.objects.get(stock_id= request.POST["spares"])

    sr.save()

    return JsonResponse({"pk": sr.pk,
                        "success":True})


def parse_csv_file(request):
    """Asynchronous way of importing data as csv.
    
    Input:
        csv_file-> the local path to the file to be imported.
        consider changing to a file that is uploaded.
        
    Output:
        None - the application starts a new thread and calls the parse_file funtion which iterates over the whole file and classifies the data according to the unique ids that follow some regular pattern."""
    
    file = request.FILES.get("csv_file")
    #print dir(file)
    if not file.name.endswith(".csv"):
        return render(request, "inv/browse.html",
                        context={"message": "You have entered an incorrect file type. Make sure the extension is '.csv'. "})    

    fil = FileSystemStorage()
    fil.save(file.name, file)
    
    global CSV_FILE_STATUS
    CSV_FILE_STATUS["running"] = True
    CSV_FILE_STATUS["start"] = time.time()
    
    if request.POST.get("data_type") == "machines":
        target = parse_file
    else:
        target = parse_spares_file
   
    CSV_RUNNING =True
    
    if not settings.TEST_CONDITIONS:
        t = threading.Thread(target=target, args=(CSV_FILE_STATUS, 
                os.path.join("media", file.name)))
        t.setDaemon(True)
        t.start()

    return HttpResponseRedirect(reverse("inventory:csv-panel"))


def get_process_updates(request):
    """Function called repeatedly to display the current status of a data import process
    
    method: GET
    
    Input: None
    Output:
        lines_run - > int
        errors -> int
        start_time -> time string
        run_time - int
        messages -> list of strings
        file_length -> int number of lines of data in total
        """
    global CSV_FILE_STATUS
    global CURRENT_CSV_THREAD
    start_time = time.strftime("%H:%M", time.localtime(
        CSV_FILE_STATUS["start"]
    ))

    run_time = 0
    if CSV_FILE_STATUS["running"]  and not CSV_FILE_STATUS["finished"]:
        run_time = time.time() - CSV_FILE_STATUS["start"]
        
    elif CSV_FILE_STATUS["finished"]:
        run_time = CSV_FILE_STATUS["stop"] - CSV_FILE_STATUS["start"]
    
    data = {"lines_run": CSV_FILE_STATUS["successful"],
            "errors": CSV_FILE_STATUS["errors"],
            "start_time": start_time,
            "run_time": int(run_time),
            "messages": CSV_FILE_STATUS["messages"],
            "file_length": CSV_FILE_STATUS["file_length"]}
            
    
    return HttpResponse(json.dumps(data), content_type="application/json")


def stop_parsing(request):
    global CSV_FILE_STATUS, CSV_RUNNING
    
    CSV_RUNNING = False
    CSV_FILE_STATUS = {"messages":[],
                    "successful": 0,
                    "errors": 0,
                    "start": 0.0,
                    "stop": 0.0,
                    "running": False,
                    "finished": False,
                    "file_length": 0,
                    }
    return HttpResponseRedirect(reverse("inventory:inventory-home"))