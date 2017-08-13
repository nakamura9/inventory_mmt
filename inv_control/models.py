from __future__ import unicode_literals

from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
class InventoryItem(models.Model):
    serial_number = models.CharField(max_length= 32, primary_key=True)
    name = models.CharField(max_length= 32)
    order_number = models.CharField(max_length=32)
    quantity = models.IntegerField()
    unit = models.CharField(max_length= 32)
    order_date = models.DateField()
    category = models.ForeignKey("inv_control.Category")
    supplier = models.CharField(max_length= 32)
    unit_price = models.FloatField()
    min_stock_level = models.IntegerField()
    reorder_quantity = models.IntegerField()


    


class Category(models.Model):
    name = models.CharField(max_length= 32)
    description = models.TextField()

    def __str__(self):
        return self.name

class Order(models.Model):
    

    def __init__(self, *args, **kwargs):
        self.actual_delivery_epoch = None
        super(Order,self).__init__(*args,**kwargs)

    order_number = models.CharField(max_length= 32)
    description = models.CharField(max_length=64)
    quantity =models.IntegerField()
    unit_price = models.FloatField()
    manufacture_date = models.DateField()
    flute_profile = models.CharField(max_length=1, choices=[
        ("a", "A Flute"),
        ("b", "B Flute"),
        ("c", "C Flute"),
    ])
    liner = models.CharField(max_length=32, choices=[
        ("kraft", "Kraft"),
    ])
    layers = models.IntegerField(choices = [
        (1, "Single Wall Board"),
        (2, "Double Wall Board"),
    ]) 
    delivery_date = models.DateField()
    customer = models.CharField(max_length= 32)
    production_status = models.CharField(max_length=32, choices=[
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed")
    ])
    delivery_status = models.CharField(max_length=16, choices = (
        ("storage", "In Storage"),
        ("transit", "In Transit"),
        ("delivered", "Delivered")
    ))

    def save(self, *args, **kwargs):
        if self.delivery_status == "delivered":
            self.actual_delivery_epoch = timezone.now().date()
        super(Order, self).save(*args, **kwargs)

    @property
    def actual_delivery_date(self):
        if self.delivery_status != "delivered":
            return "Undelivered"
        else:
            return self.actual_delivery_epoch.strftime("%d/%m/%Y")
