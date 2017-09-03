from django.shortcuts import render
from django.views.generic import TemplateView
import os
from jobcards.models import WorkOrder

class Ishikawa(TemplateView):
    template_name = os.path.join("rca", "ishikawa.html")

class RCAForm(TemplateView):
    template_name = os.path.join("rca", "rca_form.html")

    def get_context_data(self, *args, **kwargs):
        context = super(RCAForm, self).get_context_data(*args, **kwargs)
        context["breakdowns"] = WorkOrder.objects.all()
        return context