# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import threading
import time

from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.contrib.auth import authenticate

from common_base.models import Category, Account
from common_base.utilities import ajax_required, parse_file
from inv import models as inv_models


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
    print request.POST
    if authenticate(username=request.POST["username"], 
            password=request.POST["password"]):
        return HttpResponse(json.dumps({"authenticated":True}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({"authenticated":False}),
                            content_type="application/json")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def add_task(request):
    """Adds tasks to the current session
    
    Input: JSON -> "task": string
    Output: HttpResponse -> '0' or '-1'

    Adds each task to a list called 'tasks' in the current session
    Afterwards force updates the session
    """
    if request.POST != "":
        request.session["tasks"].append(request.POST["task"])
        request.session.modified = True
        return HttpResponse("0")
    else:
        return HttpResponse("-1")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def remove_task(request):
    """Removes a task from the session and the database if stored
    
    Input: JSON -> "task":string
    Output: HttpResponse '0' or '-1' 
    """

    if request.POST == "" or \
        "tasks" not in request.session:
        return HttpResponse("-1")

    if request.POST["task"] in request.session["tasks"]:
        request.session["tasks"].pop(request.POST["task"])
        request.session.modified = True
    try:
        Task.objects.get(description=request.POST["task"]).delete()
    except:#specify the exception 
        pass

    return HttpResponse("0")

@csrf_exempt
@ajax_required(HttpResponseBadRequest)
def get_combos(request):
    s = request.POST.get("str", None)
    _model = request.POST.get("model", None)

    
    if s and _model:
        items = []
        if _model == "account":
            items += get_account(s)
            
        elif _model == "component":
            items += [c.component_name for c in get_component(s)]
        
        elif _model == "spares":
            items += [sp.stock_id for sp in get_spares(s)]
        
        elif _model == "inv":
            # the third element is used client side to select the detail view
            items += [[c.pk, c.component_name, c.machine.machine_name, 0] for c in  get_component(s)]
            items += [[sp.pk, sp.stock_id, sp.name, 1] for sp in get_spares(s)]
            items += [[sa.pk, sa.unit_name, sa.machine.machine_name, 2] for sa in get_subassy(s)]    


        return HttpResponse(json.dumps({"matches":items}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"matches": []}))


def get_component(name):
    items = []
    items += [c for c in inv_models.Component.objects.filter(component_name__startswith=name)]
    items += [c for c in inv_models.Component.objects.filter(unique_id__startswith=name) if c not in items] 
    return items

def get_subassy(name):
    return [sa for sa in inv_models.SubAssembly.objects.filter(unit_name__startswith=name)]

def get_spares(name):
    items = []
    items += [sp for sp in inv_models.Spares.objects.filter(stock_id__startswith=name)]
    items += [sp for sp in inv_models.Spares.objects.filter(name__startswith=name) if sp not in items] 
    return items

def get_account(name):
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

def parse_csv_file(request):
    file_name = request.POST.get("csv_file")
    if not file_name.endswith(".csv"):
        return render(request, "inv/browse.html",
                        context={"message": "You have entered an incorrect file type. Make sure the extension is '.csv'. "})    

    
    global CSV_FILE_STATUS
    CSV_FILE_STATUS["running"] = True
    CSV_FILE_STATUS["start"] = time.time()
   
    t = threading.Thread(target=parse_file, args=(CSV_FILE_STATUS, file_name))
    t.setDaemon(True)
    t.start()

    return HttpResponseRedirect(reverse("inventory:csv-panel"))

def get_run_data(request):
    global CSV_FILE_STATUS
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
            "run_time": run_time,
            "messages": CSV_FILE_STATUS["messages"],
            "file_length": CSV_FILE_STATUS["file_length"]}
            
    
    return HttpResponse(json.dumps(data), content_type="application/json")

