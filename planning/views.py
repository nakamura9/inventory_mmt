from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import TemplateView
import os
import datetime
import calendar_objects


class MonthView(TemplateView):
    template_name=os.path.join("planning","month_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(MonthView, self).get_context_data(*args, **kwargs)
        _month = calendar_objects.Month(int(self.kwargs["year"]), int(self.kwargs["month"]),
                                    calendar_objects.MaintenanceDay)
        _month.get_month_agenda()
        print _month.month_matrix
        context["month"] = _month
        return context


class WeekView(TemplateView):
    template_name=os.path.join("planning","week_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(WeekView, self).get_context_data(*args, **kwargs)
        week = calendar_objects.Week(int(self.kwargs["year"]), int(self.kwargs["month"]), 
                    int(self.kwargs["week"]), calendar_objects.MaintenanceDay)
        week.get_week_agenda()
        context["week"] = week
        return context


class DayView(TemplateView):
    template_name=os.path.join("planning","day_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(DayView, self).get_context_data(*args, **kwargs)
        _day = datetime.date(int(self.kwargs["year"]),
                                        int(self.kwargs["month"]),
                                        int(self.kwargs["day"]))
        day = calendar_objects.MaintenanceDay(_day)
        day.get_agenda()
        context["day"] =day 
        return context

