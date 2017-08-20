# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
import os
from inv.models import Order
from django.utils import timezone
import datetime
import calendar_objects


class MonthView(TemplateView):
    template_name = os.path.join("production_calendar", "month.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MonthView, self).get_context_data(*args, **kwargs)
        month = calendar_objects.Month(int(self.args[0]), 
                            int(self.args[1]), calendar_objects.ProductionDay)
        month.get_month_agenda()
        context["month"] = month.month_agenda
        return context


class WeekView(TemplateView):
    template_name = os.path.join("production_calendar", "week.html")

    def get_context_data(self, *args, **kwargs):
        context = super(WeekView, self).get_context_data(*args, **kwargs)
        week = calendar_objects.Week(int(self.args[0]), int(self.args[1]), 
                                int(self.args[2]), calendar_objects.ProductionDay)
        week.get_week_agenda()
        context["week"] = week.week_agenda
        return context


class DayView(TemplateView):
    template_name = os.path.join("production_calendar", "day.html")

    def get_context_data(self, *args, **kwargs):
        context = super(DayView, self).get_context_data(*args, **kwargs)
        date = datetime.date(int(self.args[0]), int(self.args[1]), int(self.args[2]))
        day = calendar_objects.ProductionDay(date)
        day.get_agenda()
        context["day"] = day
        return context

