# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect,
                        HttpResponseBadRequest
from django.contrib.auth import authenticate

from common_base.models import Category
from common_base.utilities import ajax_required
from inv import models as inv_models

"""The views that correspond to the URLS """

@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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

@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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


@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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


@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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

@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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

@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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


@ajax_required(HttpResponseBadRequest)
@csrf_exempt
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


def add_category(request):
    """Quick addition of categories to the database."""

    if request.method == "POST":
        data = request.POST.copy().dict()
        data.pop("csrfmiddlewaretoken")
        Category(**data).save()
        return HttpResponse("0")


