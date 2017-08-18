from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
import os

# Create your views here.
class Home(TemplateView):
    template_name = os.path.join("machine_learning", "home.html")


class RegressionView(TemplateView):
    template_name = os.path.join("machine_learning", "regression.html")


class ClassificationView(TemplateView):
    template_name = os.path.join("machine_learning", "classifier.html")


class ClusterView(TemplateView):
    template_name = os.path.join("machine_learning", "cluster.html")

