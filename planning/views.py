from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import TemplateView
import os
import datetime
import calendar_objects


class maintenanceMonthView(TemplateView):
    template_name=os.path.join("planning","month_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceMonthView, self).get_context_data(*args, **kwargs)
        _month = calendar_objects.Month(int(self.kwargs["year"]), int(self.kwargs["month"]),
                                    calendar_objects.MaintenanceDay)
        _month.get_month_agenda()
        context["mode"] = "maintenance"
        context["month"] = _month
        return context


class maintenanceWeekView(TemplateView):
    template_name=os.path.join("planning","week_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceWeekView, self).get_context_data(*args, **kwargs)
        week = calendar_objects.Week(int(self.kwargs["year"]), int(self.kwargs["month"]), 
                    int(self.kwargs["week"]), calendar_objects.MaintenanceDay)
        week.get_week_agenda()
        context["week"] = week
        context["mode"] = "maintenance"
        return context


class maintenanceDayView(TemplateView):
    template_name=os.path.join("planning","day_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceDayView, self).get_context_data(*args, **kwargs)
        _day = datetime.date(int(self.kwargs["year"]),
                                        int(self.kwargs["month"]),
                                        int(self.kwargs["day"]))
        day = calendar_objects.MaintenanceDay(_day)
        day.get_agenda()
        context["day"] =day 
        context["mode"] = "maintenance"
        return context


class productionMonthView(TemplateView):
    template_name=os.path.join("planning","month_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionMonthView, self).get_context_data(*args, **kwargs)
        _month = calendar_objects.Month(int(self.kwargs["year"]), int(self.kwargs["month"]),
                                    calendar_objects.ProductionDay)
        _month.get_month_agenda()
        context["month"] = _month
        context["mode"] = "production"
        return context


class productionWeekView(TemplateView):
    template_name=os.path.join("planning","week_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionWeekView, self).get_context_data(*args, **kwargs)
        week = calendar_objects.Week(int(self.kwargs["year"]), int(self.kwargs["month"]), 
                    int(self.kwargs["week"]), calendar_objects.ProductionDay)
        week.get_week_agenda()
        context["week"] = week
        context["mode"] = "production"
        return context


class productionDayView(TemplateView):
    template_name=os.path.join("planning","day_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionDayView, self).get_context_data(*args, **kwargs)
        _day = datetime.date(int(self.kwargs["year"]),
                                        int(self.kwargs["month"]),
                                        int(self.kwargs["day"]))
        day = calendar_objects.ProductionDay(_day)
        day.get_agenda()
        context["day"] =day
        context["mode"] = "production"
        return context