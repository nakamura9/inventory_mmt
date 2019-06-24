import os
from collections import namedtuple
import threading
from itertools import chain

from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

import checklists
import jobcards
from .models import *
from .forms import *
from common_base.forms import CategoryForm
from common_base.models import Account, Category
from common_base.utilities import role_test
from checklists.models import Checklist
from jobcards.models import PreventativeTask, WorkOrder


class invHome(UserPassesTestMixin,TemplateView):
    """
    Landing page for all inventory related content
    """
    template_name = os.path.join("inv", "inv_home.html")
    login_url ="/login/"
    def test_func(self):
        return role_test(self.request.user)


class CSVPanel(TemplateView):
    template_name = os.path.join("inv", "engineering_inventory", "csv_panel.html")

class EngineeringInventoryView(UserPassesTestMixin , TemplateView):
    """
    Main page for all engineering inventory adjustments.
    """
    template_name = os.path.join("inv", "browse.html")
    login_url ="/login/"
    def test_func(self):
        return role_test(self.request.user)


    def get_context_data(self, *args, **kwargs):
        context = super(EngineeringInventoryView, self).get_context_data(*args, **kwargs)
        context["machines"] = Machine.objects.all()
        return context


###############################################################################
#                      Engineering Inventory Creation                         #
###############################################################################

class AssetCreate(CreateView):
    """Asset creation view"""
    template_name = os.path.join("inv", "engineering_inventory", 
        "create_update","addasset.html") 
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory:inventory-home")

class AssetUpdate(UpdateView):
    """Asset Update view"""
    template_name = os.path.join("inv","engineering_inventory", "create_update",    "addasset.html") 
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory:inventory-home")

class AssetDetail(DetailView):
    """Asset Details view"""
    template_name = os.path.join("inv","engineering_inventory", "details", "asset_detail.html") 
    model = Asset

class SparesCreate(CreateView):
    """Spares creation view"""
    template_name = os.path.join("inv","engineering_inventory", "create_update",    "addspares.html") 
    model = Spares
    form_class = SparesForm
    success_url = reverse_lazy("inventory:inventory-home")

    def form_invalid(self, form):
        return super(SparesCreate, self).form_invalid(form)

class SparesListView(ListView):
    paginate_by = 20
    model = Spares
    template_name = os.path.join("inv", "engineering_inventory", "list",            "spares_list.html")

    def get_queryset(self, *args, **kwargs):
        sort = self.request.GET.get("sort_by", None)
        search = self.request.GET.get("search", None)
        #machine = self.request.GET.get("machine", None)
        linked_only = self.request.GET.get("show_linked_only", None)
        queryset = None
        
        if search:
            return self.model.objects.filter(stock_id=search)
        if sort:
            queryset = self.model.objects.all().order_by(sort)

        if linked_only == "on":
            if queryset:
                queryset = queryset.filter(component__gt=0)
            else:
                queryset = self.model.objects.filter(component_set__gt=0)
        
        #why?
        """if machine:
            if queryset:
                queryset = queryset.filter()
            else:
                queryset = self.model.objects.filter(component_set__gt=0) 
            l = []
            for s in queryset:
                for c in s.component_set.all():
                    if c.machine.pk == machine:
                        l.append(s)

            queryset = chain(l)"""

        

        if len(list(self.request.GET.items())) == 1 and self.request.GET.get("page", None):
            queryset = self.model.objects.all()
        if len(list(self.request.GET.items())) == 0:
            queryset = self.model.objects.all()

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(SparesListView, self).get_context_data(*args, **kwargs)
        context["spares_filter_form"] = SparesFilterForm
        context["current_filters"] = "&".join([i[0]+"="+i[1] for i in self.request.GET.items() if i[0] != "page"])
        return context

class SparesUpdate(UpdateView):
    """Spares Updating view"""
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addspares.html") 
    model = Spares
    form_class = SparesForm
    success_url = reverse_lazy("inventory:inventory-home")

class SparesDetail(DetailView):
    """Spares details view"""
    template_name = os.path.join("inv", "engineering_inventory", "details","spares_detail.html") 
    model = Spares

class MachineCreateView(UserPassesTestMixin, CreateView):
    """Machine Create View"""
    template_name = os.path.join("inv", "engineering_inventory", 
        "create_update","addmachine.html") 
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"
    def test_func(self):
        return role_test(self.request.user)

    def get_context_data(self):
        context = super(MachineCreateView, self).get_context_data()
        context["run_data_form"] = RunDataForm()
        #flag used int add_run_data template
        context["edit"] = False
        return context

class SubUnitCreateView(UserPassesTestMixin,CreateView):
    """SubUnit create view"""

    template_name = os.path.join("inv", "engineering_inventory", 
        "create_update","addsubunit.html")
    model = SubUnit
    form_class = SubUnitForm
    
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"
    def test_func(self):
        return role_test(self.request.user)

class SectionCreateView(UserPassesTestMixin,CreateView):
    """Section create view"""

    template_name = os.path.join("inv", "engineering_inventory", 
        "create_update", "addsection.html")
    model = Section
    form_class = SectionForm
    
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"
    def test_func(self):
        return role_test(self.request.user)

    def get_context_data(self):
        context = super(SectionCreateView, self).get_context_data()
        context["title"] = "Section"
        return context


class SectionUpdateView(UserPassesTestMixin,UpdateView):
    """Section update view"""
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsection.html")
    model = Section
    form_class = SectionForm  
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)

    def get_context_data(self):
        context = super(SectionUpdateView, self).get_context_data()
        context["title"] = "Section"
        return context


class SubAssyCreateView(UserPassesTestMixin,CreateView):
    """SubAssembly create view"""
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addsubassy.html")
    model = SubAssembly
    form_class = SubAssyForm
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"
    
    def test_func(self):
        return role_test(self.request.user)


class PlantCreateView(UserPassesTestMixin,CreateView):
    """Plant create view"""
    template_name = os.path.join("inv", "engineering_inventory", 
        "create_update","addplant.html")
    model = Plant
    fields = ["plant_name"]
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"
    
    def test_func(self):
        return role_test(self.request.user)


class ComponentCreateView(UserPassesTestMixin,CreateView):
    """Component create view"""
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    model = Component
    form_class = ComponentForm
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)

    def post(self, *args, **kwargs):
        resp = super(ComponentCreateView, self).post(*args, **kwargs)
        if self.request.POST.get("spares_data", None):
            cmp = Component.objects.get(pk=self.request.POST["unique_id"])
            sp=Spares.objects.get(
                stock_id=self.request.POST["spares_data"])
            cmp.spares_data.add(sp)

        return resp

class ComponentEditView(UserPassesTestMixin,UpdateView):
    """Component update view"""
    model = Component
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    form_class = ComponentForm
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)

    def post(self, *args, **kwargs):
        resp = super(ComponentEditView, self).post(*args, **kwargs)
        if self.request.POST.get("spares_data", None):
            cmp = self.get_object()
            cmp.spares_data = Spares.objects.get(stock_id=self.request.POST["spares_data"])
            cmp.save()

        return resp

class MachineEditView(UserPassesTestMixin,UpdateView):
    """Machine update view"""
    model = Machine
    template_name = os.path.join("inv", "engineering_inventory", "create_update","update_machine.html")
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)

    def get_context_data(self):
        context = super(MachineEditView, self).get_context_data()
        context["run_data_form"] = RunDataForm()
        context["edit"] = True
        return context

class SubAssyEditView(UserPassesTestMixin,UpdateView):
    """SubAssembly update view"""
    model = SubAssembly
    form_class = SubAssyForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubassy.html")
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)


class SubunitEditView(UserPassesTestMixin,UpdateView):
    """SubUnit update view"""
    model = SubUnit
    form_class = SubUnitForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubunit.html")
    success_url = reverse_lazy("inventory:inventory-home")
    login_url ="/login/"

    def test_func(self):
        return role_test(self.request.user)

class RunDataUpdateView(UserPassesTestMixin, UpdateView):
    model =RunData
    form_class = RunDataUpdateForm
    template_name = os.path.join("inv", "engineering_inventory",
        "create_update", "update_rundata.html")
    login_url = "/login/"
    success_url = reverse_lazy("inventory:inventory-home")

    def test_func(self):
        return role_test(self.request.user)
###############################################################################
#                      Engineering Inventory Details                          #
###############################################################################


class MachineView(DetailView):
    """Machine detail view.
    
    Context populated with breakdown history, checklist data and planned jobs.
    """
    template_name = os.path.join("inv","engineering_inventory", "details", 
        "machine_details.html")
    model = Machine 
     
    def get_context_data(self, *args, **kwargs):
        context = super(MachineView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(
            machine=self.object, scheduled_for__gte=datetime.date.today())
        context["planned_jobs"] = [
            Planned(job.scheduled_for, 
            job.assignments.first(),
            job.estimated_labour_time, "Planned Job") \
                for job in planned_for_machine]
        checklist_on_machine = Checklist.objects.filter(machine = self.object, )
        
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(
                    Planned(check.creation_date, 
                        check.resolver, 
                         check.estimated_time,
                         "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")
        unplanned_job_on_machine = WorkOrder.objects.filter(machine = self.object)
                
        context["unplanned_jobs"] = [
            UnPlanned(b.execution_date, b.assigned_to,
                 b.description, b.status) \
                    for b in unplanned_job_on_machine]        
        return context


class SubUnitView(DetailView):
    """
    Provides data concerning a particular subunit
    """
    template_name = os.path.join("inv", "engineering_inventory", "details", 
        "subunit_details.html")
    model = SubUnit


class SectionDetailView(DetailView):
    """Section detail view.
    
    Context populated with breakdown history, checklist data and planned jobs.
    """
    model = Section
    template_name = os.path.join("inv","engineering_inventory", "details", "section_details.html")

    def get_context_data(self, *args, **kwargs):
        context = super(SectionDetailView, self).get_context_data(
            *args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(
            section=self.object, completed_date = None)
        context["planned_jobs"] = [
            Planned(job.scheduled_for, job.assignments.first(),
                job.estimated_downtime, "Planned Job") \
                    for job in planned_for_machine]

        checklist_on_machine = Checklist.objects.filter(section = self.object) 
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(
                    Planned(check.next, 
                        check.resolver, 
                        check.estimated_time,
                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")
        unplanned_job_on_machine = WorkOrder.objects.filter(
            section = self.object)                
        context["unplanned_jobs"] = [
            UnPlanned(b.execution_date, b.assigned_to, b.description, b.status)\
                for b in unplanned_job_on_machine]
        return context


class ComponentView(DetailView):
    """
    Provides data concerning components
    """
    template_name = os.path.join("inv", "engineering_inventory", "details", "component_details.html")
    model = Component


class SubAssyView(DetailView):
    """
    Provides data concerning subassemblies
    """
    template_name = os.path.join("inv", "engineering_inventory", "details","subassy_details.html")
    model = SubAssembly
    
    
###############################################################################
#                      Production inventory                                   #
###############################################################################

###############################################################################
#                               Delete Views                                  #                              
###############################################################################


def delete_component(request, pk):
    """Deletes a Component specified by pk, raises 404 if not found"""

    get_object_or_404(Component, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_subassembly(request, pk):    
    """Deletes a SubAssembly specified by pk, raises 404 if not found"""

    get_object_or_404(SubAssembly, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_section(request, pk):    
    """Deletes a Section specified by pk, raises 404 if not found"""

    get_object_or_404(Section, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_subunit(request, pk):
    """Deletes a SubUnit specified by pk, raises 404 if not found"""

    get_object_or_404(SubUnit, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))


def delete_machine(request, pk):
    """Deletes a Machine specified by pk, raises 404 if not found"""

    get_object_or_404(Machine, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

'''def delete_order(request, pk):
    """Deletes an Order specified by pk, raises 404 if not found"""

    get_object_or_404(Order, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))
'''
def delete_run_data(request, pk=None, mech_pk=None):
    get_object_or_404(RunData, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:edit_machine", kwargs={"pk":mech_pk}))
