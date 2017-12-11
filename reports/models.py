from __future__ import unicode_literals

from django.db import models

class Report(models.Model):
    created = models.DateField(auto_now=True)
    author = models.ForeignKey("common_base.Account", related_name="%(class)s_author")
    target = models.ManyToManyField("common_base.Account", related_name="%(class)s_target")#dont change
    start_period = models.DateField()
    end_period = models.DateField()
    scope = models.CharField(max_length=32)
    machine = models.ManyToManyField("inv.Machine")
    section = models.ManyToManyField("inv.Section")
    subunit = models.ManyToManyField("inv.SubUnit")
    subassembly = models.ManyToManyField("inv.SubAssembly")
    component = models.ManyToManyField("inv.Component")
    spares = models.ManyToManyField("inv.Spares")
    spares_category = models.ManyToManyField("common_base.Category", related_name="%(class)s_spares_category")
    comments = models.ManyToManyField("common_base.Comment")

