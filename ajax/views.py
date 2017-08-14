# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from inv import models as inv_models
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect
import json
from django.contrib.auth import authenticate

@csrf_exempt
def update_subunit(request):
    if not request.is_ajax() and \
        request.POST.get("machine", None) == None:
        return Http404()
    
    machine =inv_models.Machine.objects.get(pk= \
                        request.POST["machine"])
    units = [[unit[0],unit[1]] for unit in machine.subunit_set.values_list()]
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