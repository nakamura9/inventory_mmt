# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,reverse
from django.forms import ModelChoiceField
from django.views.generic import TemplateView

from .forms import userForm
from .models import Account
from inv.models import Machine

class AboutTemplateView(TemplateView):
    template_name = os.path.join("common_base", "about.html")

def test_features(request):
    return render(request, os.path.join("common_base", "test.html"), )


def login(request):
    """Login view for the application.
    
    GET: 'login.html'
    
    POST: 
        Input: username and password
        Output: Successful 'maintenance:machine-overview'
                Failed redirect back to the login page"""
    
    if request.method == "GET":
       return render(request, os.path.join("common_base", "login.html"))
    
    else:
        name = request.POST["name"]
        pwd = request.POST["pwd"]
        user= authenticate(username=name, password=pwd)
        if user:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("maintenance:machine-overview"))
        else:
            return HttpResponseRedirect(reverse("login"))


def sign_up(request):
    """Sign up page for new users.
    
    GET: 'signup.html'
    POST:
        success: 'login' page.
        failure: signup page with error."""
    
    if request.method == "GET":
        form = userForm()
        return render(request, os.path.join("common_base", "signup.html"), context={"form": form})
    else:
        form = userForm(request.POST)
        if form.is_valid():
            try:
                if form.cleaned_data["role"] == "admin":
                    raise Exception("You cannot create this type of account from this form")
                new_user = Account.objects.create_user(**form.cleaned_data)
                new_user.save()
            except Exception as e:
                return render(request, os.path.join("common_base", "signup.html"),
                                 context={"form": form,
                                        "message": e})

            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            return render(request, os.path.join("common_base", "signup.html"), context={"form": form})

def logout(request):
    """Function used to logout users without an associated page
    
    #add js dialog box next time.

    always returns the login page."""
    
    if request.user.is_authenticated:
        auth_logout(request)

    return HttpResponseRedirect(reverse("login"))