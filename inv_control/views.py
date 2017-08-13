from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls import reverse
import os
from .forms import *
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from inv.models import *

def show(period= "1"):
    
    return HttpResponseRedirect(reverse("client:browse"))

####################################################################
#Production inventory                                              #
####################################################################



#**************
#Categories
#**************
class CategoryList(ListView):
    model = Category
    context_object_name = 'categories'
    template_name=os.path.join("inv_control", "raw_materials.html")


class categoryForm(CreateView):
    template_name = os.path.join("inv_control", "category_form.html")
    form_class = CategoryForm
    success_url = reverse_lazy("control_forms:raw-materials")


#*************************
#Inventory Items
#*************************
class inventoryItemUpdateView(UpdateView):
    model = InventoryItem
    template_name = os.path.join("inv_control", "inventory_item.html")
    success_url = reverse_lazy("control_forms:raw-materials")
    form_class = InventoryItemForm


class inventoryItemFormView(CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = os.path.join("inv_control", "inventory_item.html")
    success_url = reverse_lazy("control_forms:raw-materials")


class inventoryItemDetailView(DetailView):
    model = InventoryItem
    template_name= os.path.join("inv_control", "inventory_item_details.html")
    

class inventoryListView(TemplateView):
    template_name = os.path.join("inv_control","inventory_list.html")

    def get_context_data(self, *args, **kwargs):
        context = super(inventoryListView, self).get_context_data(*args, **kwargs)
        category = Category.objects.get(name=self.kwargs["filter"])
        context["items"] = InventoryItem.objects.filter(category = category)
        context["category"] = category 
        return context


#***********************
#Finished Prodcuts
#***********************
class OrderCreateView(CreateView):
    form_class = OrderForm
    success_url = reverse_lazy("control_forms:raw-materials")
    template_name = os.path.join("inv_control", "order_form.html")


class OrderUpdateView(UpdateView):
    form_class = OrderForm
    success_url = reverse_lazy("control_forms:raw-materials")
    template_name = os.path.join("inv_control", "order_form.html")
    model = Order

class OrderList(ListView):
    model = Order
    template_name= os.path.join("inv_control", "orders_list.html")


class OrderDetailView(DetailView):
    model = Order
    template_name = os.path.join("inv_control", "orders_detailview.html")


#############################################################################
# engineering inventory                                                     #
#############################################################################

class machineView(CreateView):
    template_name = os.path.join("inv_control", "addmachine.html") 
    model = Machine
    form_class = MachineForm
    success_url = reverse_lazy("client:browse")
    

class subunitView(CreateView):
    template_name = os.path.join("inv_control", "addsubunit.html")
    model = SubUnit
    form_class = SubUnitForm
    
    success_url = reverse_lazy("client:browse")

class subassyView(CreateView):
    template_name = os.path.join("inv_control", "addsubassy.html")
    model = SubAssembly
    form_class = SubAssyForm
    
    success_url = reverse_lazy("client:browse")

class plantView(CreateView):
    template_name = os.path.join("inv_control", "addplant.html")
    model = Plant
    fields = ["plant_name"]
    success_url = reverse_lazy("client:browse")

class componentView(CreateView):
    template_name = os.path.join("inv_control", "addcomponent.html")
    model = Component
    form_class = ComponentForm
    
    success_url = reverse_lazy("client:browse")


class componentEditView(UpdateView):
    model = Component
    template_name = os.path.join("inv_control", "addcomponent.html")
    form_class = ComponentForm


class machineEditView(UpdateView):
    model = Machine
    template_name = os.path.join("inv_control", "addmachine.html")
    form_class = MachineForm
    success_url = reverse_lazy("client:browse")


class subassyEditView(UpdateView):
    model = SubAssembly
    form_class = SubAssyForm
    template_name = os.path.join("inv_control", "addsubassy.html")
    

class subunitEditView(UpdateView):
    model = SubUnit
    form_class = SubUnitForm
    template_name = os.path.join("inv_control", "addsubunit.html")

class browseView(TemplateView):
    template_name = os.path.join("inv_control", "browse.html")
    
    def get_context_data(self, *args, **kwargs):
        context = super(browseView, self).get_context_data(*args, **kwargs)
        context["machines"] = Machine.objects.all()
        return context

#############################################################################
#delete views                                                               #
#############################################################################
def delete_component(request, pk):
    Component.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("control_forms:browse"))

def delete_subassembly(request, pk):    
    SubAssembly.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("control_forms:browse"))


def delete_subunit(request, pk):    
    SubUnit.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("control_forms:browse"))


def delete_machine(request, pk):
    Machine.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("control_forms:browse"))

def delete_order(request, pk):
    Order.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("control_forms:finished-products-list"))