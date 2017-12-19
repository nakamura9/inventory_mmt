# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import threading
import time
import datetime

from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.contrib.auth import authenticate
from django.core import serializers
from django.http import JsonResponse

from common_base.models import Category, Account
from common_base.utilities import ajax_required, parse_file, parse_spares_file
from common_base.feature_testing import parse_file as pf
from inv import models as inv_models
from inv.forms import RunDataForm
from jobcards.models import SparesRequest


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

@csrf_exempt
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
    """request is made by ajax"""
    data = RunDataForm(request.POST)
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
    if pk == "*":
        equipment = inv_models.Machine.objects.all()
        
    else:
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
        items = []
        if _model == "account":
            items += get_account(s)

        elif _model == "machine":
            items += [m.machine_name for m in get_machine(s)]

        elif  _model == "section":
            items += [s.section_name for s in get_section(s)]

        elif _model == "subunit":
            items += [s.unit_name for s in get_subunit(s)]

        elif _model == "subassembly":
            items += [s.unit_name for s in get_subassy(s)]

        elif _model == "component":
            items += [c.component_name for c in get_component(s)]
        
        elif _model == "spares":
            items += [sp.stock_id for sp in get_spares(s)]
        
        elif _model == "inv":
            # the third element is used client side to select the detail view
            items += [[c.pk, c.component_name, c.machine.machine_name, 0] for c in  get_component(s)]
            items += [[sp.pk, sp.stock_id, sp.name, 1] for sp in get_spares(s)]
            items += [[sa.pk, sa.unit_name, sa.machine.machine_name, 2] for sa in get_subassy(s)]    


        if len(items) > 20:
            items = items[:20]
            
        return HttpResponse(json.dumps({"matches":items}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"matches": []}))

def get_machine(name):
    items = []
    items += [m for m in inv_models.Machine.objects.filter(pk__startswith=name)]
    items += [m for m in inv_models.Machine.objects.filter(machine_name__contains=name) if m not in items ]
    

    return items

def get_section(name):
    items = []
    items += [s for s in inv_models.Section.objects.filter(pk__startswith=name)]
    items += [s for s in inv_models.Section.objects.filter(section_name__contains=name) if s not in items]
    
    return items 

def get_subunit(name):
    items = []
    items += [s for s in inv_models.SubUnit.objects.filter(pk__startswith=name)]
    items += [s for s in inv_models.SubUnit.objects.filter(unit_name__startswith=name) if s not in items ]
    
    return items 

def get_subassy(name):
    """Searches subassemblies by name"""

    return [sa for sa in inv_models.SubAssembly.objects.filter(unit_name__startswith=name)]

def get_component(name):
    """Searches a component by name, and id"""

    items = []
    items += [c for c in inv_models.Component.objects.filter(component_name__startswith=name)]
    items += [c for c in inv_models.Component.objects.filter(unique_id__startswith=name) if c not in items] 
    return items



def get_spares(name):
    """searches spares by name and stock_id """
    items = []
    items += [sp for sp in inv_models.Spares.objects.filter(stock_id__startswith=name)]
    items += [sp for sp in inv_models.Spares.objects.filter(name__startswith=name) if sp not in items] 
    return items

def get_account(name):
    """Searches accounts by username, first name and last name"""
    items = []
    items += [a.username  for a in Account.objects.filter(
                username__startswith=name)]
    items += [a.username  for a in Account.objects.filter(
                first_name__startswith=name) if a.username not in items]
    items += [a.username  for a in Account.objects.filter(
                last_name__startswith=name) if a.username not in items]
    
    return items


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

    file_name = request.POST.get("csv_file")
    if not file_name.endswith(".csv"):
        return render(request, "inv/browse.html",
                        context={"message": "You have entered an incorrect file type. Make sure the extension is '.csv'. "})    

    
    global CSV_FILE_STATUS
    CSV_FILE_STATUS["running"] = True
    CSV_FILE_STATUS["start"] = time.time()
    
    if request.POST.get("data_type") == "machines":
        target = parse_file
    else:
        target = parse_spares_file
        
    t = threading.Thread(target=target, args=(CSV_FILE_STATUS, file_name))
    t.setDaemon(True)
    t.start()

    return HttpResponseRedirect(reverse("inventory:csv-panel"))


def get_run_data(request):
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