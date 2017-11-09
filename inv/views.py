import os
from collections import namedtuple


from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

import checklists
import jobcards
from .models import *
from .forms import *
from common_base.forms import CategoryForm
from common_base.models import Account, Category
from checklists.models import Checklist
from jobcards.models import PreventativeTask, WorkOrder


class invHome(TemplateView):
    """
    Landing page for all inventory related content
    """
    template_name = os.path.join("inv", "inv_home.html")
    
class EngineeringInventoryView(TemplateView):
    """
    Main page for all engineering inventory adjustments.
    """
    template_name = os.path.join("inv", "browse.html")
    
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

    template_name = os.path.join("inv","engineering_inventory", "create_update", "addasset.html") 
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory:inventory-home")

class AssetDetail(DetailView):
    """Asset Details view"""

    template_name = os.path.join("inv","engineering_inventory", "details", "asset_detail.html") 
    model = Asset

class SparesCreate(CreateView):
    """Spares creation view"""

    template_name = os.path.join("inv","engineering_inventory", "create_update",                                 "addspares.html") 
    model = Spares
    form_class = SparesForm
    success_url = reverse_lazy("inventory:inventory-home")

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

class MachineCreateView(CreateView):
    """Machine Create View"""

    template_name = os.path.join("inv", "engineering_inventory", "create_update","addmachine.html") 
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")
    

class SubUnitCreateView(CreateView):
    """SubUnit create view"""

    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubunit.html")
    model = SubUnit
    form_class = SubUnitForm
    
    success_url = reverse_lazy("inventory:inventory-home")


class SectionCreateView(CreateView):
    """Section create view"""

    template_name = os.path.join("inv", "engineering_inventory", 
    "create_update", "addsection.html")
    model = Section
    form_class = SectionForm
    
    success_url = reverse_lazy("inventory:inventory-home")

    def get_context_data(self):
        context = super(sectionView, self).get_context_data()
        context["title"] = "Section"
        return context


class SectionUpdateView(UpdateView):
    """Section update view"""

    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsection.html")
    model = Section
    form_class = SectionForm
    
    success_url = reverse_lazy("inventory:inventory-home")

    def get_context_data(self):
        context = super(sectionUpdateView, self).get_context_data()
        context["title"] = "Section"
        return context


        

class SubAssyCreateView(CreateView):
    """SubAssembly create view"""

    template_name = os.path.join("inv","engineering_inventory", "create_update", "addsubassy.html")
    model = SubAssembly
    form_class = SubAssyForm
    
    success_url = reverse_lazy("inventory:inventory-home")

class PlantCreateView(CreateView):
    """Plant create view"""

    template_name = os.path.join("inv", "engineering_inventory", "create_update","addplant.html")
    model = Plant
    fields = ["plant_name"]
    success_url = reverse_lazy("inventory:inventory-home")

class ComponentCreateView(CreateView):
    """Component create view"""

    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    model = Component
    form_class = ComponentForm
    
    success_url = reverse_lazy("inventory:inventory-home")


class ComponentEditView(UpdateView):
    """Component update view"""

    model = Component
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    form_class = ComponentForm


class MachineEditView(UpdateView):
    """Machine update view"""

    model = Machine
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addmachine.html")
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")


class SubAssyEditView(UpdateView):
    """SubAssembly update view"""

    model = SubAssembly
    form_class = SubAssyForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","adFdsubassy.html")
    

class SubunitEditView(UpdateView):
    """SubUnit update view"""

    model = SubUnit
    form_class = SubUnitForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubunit.html")


###############################################################################
#                      Engineering Inventory Details                          #
###############################################################################


class MachineView(DetailView):
    """Machine detail view.
    
    Context populated with breakdown history, checklist data and planned jobs.
    """
    template_name = os.path.join("inv","engineering_inventory", "details", "machine_details.html")
    model = Machine 
     
    def get_context_data(self, *args, **kwargs):
        context = super(MachineView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(machine=self.object, 
                                                    completed_date=None)
        context["planned_jobs"] = [Planned(job.creation_epoch, job.resolver,
                                        job.estimated_time, "Planned Job") for job in planned_for_machine]
        checklist_on_machine = Checklist.objects.filter(machine = self.object)
        
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(Planned(check.creation_date, 
                                                        check.resolver, 
                                                        check.estimated_time,
                                                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")

        unplanned_job_on_machine = WorkOrder.objects.filter(machine = self.object)
        
        
        context["unplanned_jobs"] = [UnPlanned(b.execution_date, b.assigned_to.first, b.description, b.status) \
                                    for b in unplanned_job_on_machine]

        
        return context


class SubUnitView(DetailView):
    """
    Provides data concerning a particular subunit
    """

    template_name = os.path.join("inv", "engineering_inventory", "details", "subunit_details.html")
    model = SubUnit


class SectionDetailView(DetailView):
    """Section detail view.
    
    Context populated with breakdown history, checklist data and planned jobs.
    """
    
    model = Section
    template_name = os.path.join("inv","engineering_inventory", "details", "section_details.html")

    def get_context_data(self, *args, **kwargs):
        context = super(sectionDetailView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(section=self.object, completed_date = None)
        context["planned_jobs"] = [Planned(job.execution_date, job.resolver,
                                        job.estimated_time, "Planned Job") \
                                        for job in planned_for_machine]

        checklist_on_machine = Checklist.objects.filter(section = self.object)
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(Planned(check.creation_date, 
                                                        check.resolver, 
                                                        check.estimated_time,
                                                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")

        unplanned_job_on_machine = WorkOrder.objects.filter(section = self.object)
                
        context["unplanned_jobs"] = [UnPlanned(b.execution_date, b.assigned_to.first, b.description, b.status) \
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


class CategoryList(ListView):
    """Category list view"""

    model = Category
    context_object_name = 'categories'
    template_name=os.path.join("inv", "production_inventory","raw_materials.html")


class CategoryCreateView(CreateView):
    """Category create view"""

    template_name = os.path.join("inv","category_form.html")
    form_class = CategoryForm
    success_url = reverse_lazy("inventory:raw-materials")


class InventoryItemUpdateView(UpdateView):
    """Inventory Item Update view"""

    model = InventoryItem
    template_name = os.path.join("inv", "production_inventory", "create_update","inventory_item.html")
    success_url = reverse_lazy("inventory:raw-materials")
    form_class = InventoryItemForm


class InventoryItemFormView(CreateView):
    """Inventory Item Create View"""

    model = InventoryItem
    form_class = InventoryItemForm
    template_name = os.path.join("inv", "production_inventory", "create_update","inventory_item.html")
    success_url = reverse_lazy("inventory:raw-materials")


class InventoryItemDetailView(DetailView):
    """Inventory Item Detail view"""

    model = InventoryItem
    template_name= os.path.join("inv","production_inventory", "details", "inventory_item_details.html")
    

class InventoryListView(TemplateView):
    """Inventory List view"""
    
    template_name = os.path.join("inv","production_inventory", "list","inventory_list.html")

    def get_context_data(self, *args, **kwargs):
        context = super(inventoryListView, self).get_context_data(*args, **kwargs)
        category = Category.objects.get(name=self.kwargs["filter"])
        context["items"] = InventoryItem.objects.filter(category = category)
        context["category"] = category 
        return context


class OrderCreateView(CreateView):
    """Order Create View"""

    form_class = OrderForm
    success_url = reverse_lazy("inventory:raw-materials")
    template_name = os.path.join("inv","production_inventory", "create_update", "order_form.html")


class OrderUpdateView(UpdateView):
    """Order Update view """

    form_class = OrderForm
    success_url = reverse_lazy("inventory:raw-materials")
    template_name = os.path.join("inv", "production_inventory", "create_update","order_form.html")
    model = Order

class OrderList(ListView):
    """Order List View"""

    model = Order
    template_name= os.path.join("inv","production_inventory", "list", "order_list.html")


class OrderDetailView(DetailView):
    """Order Detail View"""

    model = Order
    template_name = os.path.join("inv","production_inventory", "details", "orders_detailview.html")


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

def delete_order(request, pk):
    """Deletes an Order specified by pk, raises 404 if not found"""

    get_object_or_404(Order, pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))