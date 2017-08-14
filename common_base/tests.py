# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from inv import models as inv_models
from checklists import models as ch_models
from jobcards import models as jb_models
from .models import Account
import datetime

class TestDataMixin(object):
    @classmethod
    def create_test_inventory_models(cls):
        inv_models.Machine(machine_name="Test Machine",
                                unique_id="T_M",
                                manufacturer="Langston",
                                estimated_value="200000",
                                commissioning_date=datetime.date.today() \
                                - datetime.timedelta(days=500),
                                ).save()

        inv_models.SubUnit(unique_id="T_S",
                unit_name="Test SubUnit",
                machine=inv_models.Machine.objects.get(pk="T_M")).save()

        inv_models.SubAssembly(unique_id="T_SA",
                    unit_name="Test SubAssembly",
                    subunit=inv_models.SubUnit.objects.get(pk="T_S",
                    machine=inv_models.Machine.objects.get(pk="T_M"))).save()

    @classmethod
    def create_dummy_accounts(cls):
        Account(username= "Test User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="artisan").save()

        Account(username= "Test Admin User",
                first_name="Test",
                last_name="User",
                password="test123",
                role="admin").save()
