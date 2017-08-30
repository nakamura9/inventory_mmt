# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from inv import models as inv_models
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect
import json
from django.contrib.auth import authenticate

@csrf_exempt
def update_section(request):
    if not request.is_ajax() and \
        request.POST.get("machine", None) == None:
        return Http404()
    
    machine =inv_models.Machine.objects.get(pk= \
                        request.POST["machine"])
    sections = [[section[0], section[1]] for section in machine.section_set.values_list()]
    return HttpResponse(json.dumps(
            {"sections": sections}),
                content_type="application/json")


@csrf_exempt
def update_subunit(request):
    if not request.is_ajax() and \
        request.POST.get("section", None) == None:
        return Http404()
    
    section =inv_models.Section.objects.get(pk= \
                        request.POST["section"])
    units = [[unit[0],unit[1]] for unit in section.subunit_set.values_list()]
    return HttpResponse(json.dumps(
            {"units": units}),
                content_type="application/json")


@csrf_exempt
def update_subassembly(request):
    if not request.is_ajax() and \
        request.POST.get("unit", None) ==None:
        return Http404()
    
    subunit =inv_models.SubUnit.objects.get(
                    pk= request.POST["unit"])
    
    subassemblies= [[assy[0], assy[1]] for assy in subunit.subassembly_set.values_list()]
    return HttpResponse(json.dumps(
            {"subassemblies": subassemblies}),
                content_type="application/json")


@csrf_exempt
def update_components(request):
    if not request.is_ajax() and \
        request.POST.get("subassy", None) == None:
        return Http404()
    
    subassy =inv_models.SubAssembly.objects.get(
                    pk= request.POST["subassy"])
    
    components= [[comp[0],comp[1]] for comp in subassy.component_set.values_list()]
    return HttpResponse(json.dumps(
            {"components": components}),
                content_type="application/json")


@csrf_exempt
def ajaxAuthenticate(request):
    if authenticate(username=request.POST["username"], 
            password=request.POST["password"]):
        return HttpResponse(json.dumps({"authenticated":True}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({"authenticated":False}),
                            content_type="application/json")


@csrf_exempt
def add_task(request):
    if request.is_ajax():
        if request.POST != "":
            request.session["tasks"].append(request.POST["task"])
            request.session.modified = True
            return HttpResponse("0")
        else:
            return HttpResponse("-1")
    else:
        return Http404()

@csrf_exempt
def remove_task(request):
    if not request.is_ajax:
        return Http404()
    if request.POST == "" or \
        "tasks" not in request.session:
        return HttpResponse("-1")

    if request.POST["task"] in request.session["tasks"]:
        request.session["tasks"].pop(request.POST["task"])
        request.session.modified = True
    try:
        Task.objects.get(description=request.POST["task"]).delete()
    except:
        return Http404()

    return HttpResponse("0")