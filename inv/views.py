from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
import os
import checklists
import jobcards
from .models import *
from .forms import *
from common_base.forms import CategoryForm

from common_base.models import Account, Category
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from checklists.models import Checklist
from jobcards.models import PreventativeTask, WorkOrder
from collections import namedtuple


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
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addasset.html") 
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory:inventory-home")

class AssetUpdate(UpdateView):
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addasset.html") 
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory:inventory-home")

class AssetDetail(DetailView):
    template_name = os.path.join("inv","engineering_inventory", "details", "asset_detail.html") 
    model = Asset

class SparesCreate(CreateView):
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addspares.html") 
    model = Asset
    form_class = SparesForm
    success_url = reverse_lazy("inventory:inventory-home")

class SparesUpdate(UpdateView):
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addspares.html") 
    model = Asset
    form_class = SparesForm
    success_url = reverse_lazy("inventory:inventory-home")

class SparesDetail(DetailView):
    template_name = os.path.join("inv", "engineering_inventory", "details","spares_detail.html") 
    model = Spares

class machineView(CreateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addmachine.html") 
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")
    

class subunitView(CreateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubunit.html")
    model = SubUnit
    form_class = SubUnitForm
    
    success_url = reverse_lazy("inventory:inventory-home")


class sectionView(CreateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update", "addsection.html")
    model = Section
    form_class = SectionForm
    
    success_url = reverse_lazy("inventory:inventory-home")

    def get_context_data(self):
        context = super(sectionView, self).get_context_data()
        context["title"] = "Section"
        return context


class sectionUpdateView(UpdateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsection.html")
    model = Section
    form_class = SectionForm
    
    success_url = reverse_lazy("inventory:inventory-home")

    def get_context_data(self):
        context = super(sectionUpdateView, self).get_context_data()
        context["title"] = "Section"
        return context


        

class subassyView(CreateView):
    template_name = os.path.join("inv","engineering_inventory", "create_update", "addsubassy.html")
    model = SubAssembly
    form_class = SubAssyForm
    
    success_url = reverse_lazy("inventory:inventory-home")

class plantView(CreateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addplant.html")
    model = Plant
    fields = ["plant_name"]
    success_url = reverse_lazy("inventory:inventory-home")

class componentView(CreateView):
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    model = Component
    form_class = ComponentForm
    
    success_url = reverse_lazy("inventory:inventory-home")


class componentEditView(UpdateView):
    model = Component
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addcomponent.html")
    form_class = ComponentForm


class machineEditView(UpdateView):
    model = Machine
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addmachine.html")
    form_class = MachineForm
    success_url = reverse_lazy("inventory:inventory-home")


class subassyEditView(UpdateView):
    model = SubAssembly
    form_class = SubAssyForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubassy.html")
    

class subunitEditView(UpdateView):
    model = SubUnit
    form_class = SubUnitForm
    template_name = os.path.join("inv", "engineering_inventory", "create_update","addsubunit.html")


###############################################################################
#                      Engineering Inventory Details                          #
###############################################################################


class MachineView(DetailView):
    """
    Provides in depth information regarding the requested machine
    """
    template_name = os.path.join("inv","engineering_inventory", "details", "machine_details.html")
    model = Machine 
     
    def get_context_data(self, *args, **kwargs):
        context = super(MachineView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(machine=self.object, 
                                                    completed=False)
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
        
        
        context["unplanned_jobs"] = [UnPlanned(b.creation_epoch, b.resolver, b.description, b.completed) \
                                    for b in unplanned_job_on_machine]

        
        return context


class SubUnitView(DetailView):
    """
    Provides data concerning a particular subunit
    """

    template_name = os.path.join("inv", "engineering_inventory", "details", "subunit_details.html")
    model = SubUnit

    def get_context_data(self, *args, **kwargs):
        context = super(SubUnitView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(subunit=self.object, 
                                                    completed=False)
        context["planned_jobs"] = [Planned(job.creation_epoch, job.resolver,
                                        job.estimated_time, "Planned Job") for job in planned_for_machine]
        checklist_on_machine = Checklist.objects.filter(subunit = self.object)
        
        for check in checklist_on_machine:
            if check.is_open:
                context["planned_jobs"].append(Planned(check.creation_date, 
                                                        check.resolver, 
                                                        check.estimated_time,
                                                        "Checklist"))

        UnPlanned = namedtuple("UnPlanned", "date resolver description status")

        unplanned_job_on_machine = WorkOrder.objects.filter(subunit = self.object)
                
        context["unplanned_jobs"] = [UnPlanned(b.creation_epoch, b.resolver, b.description, b.completed) \
                                    for b in unplanned_job_on_machine]

        return context


class sectionDetailView(DetailView):
    model = Section
    template_name = os.path.join("inv","engineering_inventory", "details", "section_details.html")

    def get_context_data(self, *args, **kwargs):
        context = super(sectionDetailView, self).get_context_data(*args, **kwargs)
        Planned = namedtuple("Planned", "date resolver est_time type")
        planned_for_machine =PreventativeTask.objects.filter(section=self.object, 
                                                    completed=False)
        context["planned_jobs"] = [Planned(job.creation_epoch, job.resolver,
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
                
        context["unplanned_jobs"] = [UnPlanned(b.creation_epoch, b.resolver, b.description, b.completed) \
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
    model = Category
    context_object_name = 'categories'
    template_name=os.path.join("inv", "production_invetory", "create_update","raw_materials.html")


class categoryForm(CreateView):
    template_name = os.path.join("inv", "production_invetory", "create_update","category_form.html")
    form_class = CategoryForm
    success_url = reverse_lazy("inventory:raw-materials")


class inventoryItemUpdateView(UpdateView):
    model = InventoryItem
    template_name = os.path.join("inv", "production_invetory", "create_update","inventory_item.html")
    success_url = reverse_lazy("inventory:raw-materials")
    form_class = InventoryItemForm


class inventoryItemFormView(CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = os.path.join("inv", "production_invetory", "create_update","inventory_item.html")
    success_url = reverse_lazy("inventory:raw-materials")


class inventoryItemDetailView(DetailView):
    model = InventoryItem
    template_name= os.path.join("inv","production_invetory", "details", "inventory_item_details.html")
    

class inventoryListView(TemplateView):
    template_name = os.path.join("inv","production_invetory", "list","inventory_list.html")

    def get_context_data(self, *args, **kwargs):
        context = super(inventoryListView, self).get_context_data(*args, **kwargs)
        category = Category.objects.get(name=self.kwargs["filter"])
        context["items"] = InventoryItem.objects.filter(category = category)
        context["category"] = category 
        return context


class OrderCreateView(CreateView):
    form_class = OrderForm
    success_url = reverse_lazy("inventory:raw-materials")
    template_name = os.path.join("inv","production_invetory", "create_update", "order_form.html")


class OrderUpdateView(UpdateView):
    form_class = OrderForm
    success_url = reverse_lazy("inventory:raw-materials")
    template_name = os.path.join("inv", "production_invetory", "create_update","order_form.html")
    model = Order

class OrderList(ListView):
    model = Order
    template_name= os.path.join("inv","production_invetory", "list", "orders_list.html")


class OrderDetailView(DetailView):
    model = Order
    template_name = os.path.join("inv","production_invetory", "details", "orders_detailview.html")


###############################################################################
#                               Delete Views                                  #                              
###############################################################################


def delete_component(request, pk):
    Component.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_subassembly(request, pk):    
    SubAssembly.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_section(request, pk):    
    Section.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_subunit(request, pk):    
    SubUnit.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))


def delete_machine(request, pk):
    Machine.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))

def delete_order(request, pk):
    Order.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("inventory:engineering-inventory"))