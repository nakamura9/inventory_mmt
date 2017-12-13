from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import TemplateView
import os
import datetime
import calendar_objects
from .forms import MonthViewFilterForm, WeekViewFilterForm, DayViewFilterForm

def get_include(cls):
    """
    Utility function for selecting the models to include based on a filter accompanying
    the GET request.
    """
    _include = []
    if cls.request.GET.get("checklists", None) == "on":
        _include.append("checks")
    if cls.request.GET.get("planned_jobs", None) == "on":
        _include.append("jobs")

    return _include


class maintenanceMonthView(TemplateView):
    """MonthView Calender.

    uses calender_objects.Month to generate a calender based on the filtered data."""

    template_name=os.path.join("planning","month_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceMonthView, self).get_context_data(*args, 
                                                                    **kwargs)

        

        
        #fix this. if year is not set, it wont filter
        if self.request.GET.get("year", None):
            m = int(self.request.GET.get("month"))
            y = int(self.request.GET.get("year"))
            context["month_string"] = datetime.datetime.strftime(
                    datetime.date(y, m, 1),"%b, %Y")
            _month = calendar_objects.Month(y, m,                                                               calendar_objects.MaintenanceDay,
                                            include=get_include(self),
                                            filters = {"resolver":self.request.GET["resolver"],
                                                        "machine": self.request.GET["machine"]})
            
        elif self.kwargs.get("year", None):
            context["month_string"] = datetime.datetime.strftime(datetime.date(int(self.kwargs["year"]), int(self.kwargs["month"]), 1),"%b, %Y")
            today = datetime.date.today()
            _month = calendar_objects.Month(today.year, today.month,
                                            calendar_objects.MaintenanceDay,
                                            include=["checks", "jobs"])
                                            
        else:
            today =datetime.date.today()
            context["month_string"] =today
            _month = calendar_objects.Month(today.year, 
                                        today.month,
                                        calendar_objects.MaintenanceDay,include=["checks", "jobs"])
        
        _month.get_month_agenda()
        context["month"] = _month
        
        context["form"] = MonthViewFilterForm()
        return context


class maintenanceWeekView(TemplateView):
    """WeekView Calender.

    uses calender_objects.Week to generate a calender based on the filtered data."""
    
    template_name=os.path.join("planning","week_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceWeekView, self).get_context_data(*args, **kwargs)


        
        #when filtering
        if self.request.GET.get("year", None):
            week = calendar_objects.Week(int(self.request.GET.get("year")),
                                        int(self.request.GET.get("month")),
                                        int(self.request.GET.get("week")),
                                        calendar_objects.MaintenanceDay,
                                        include= get_include(self),
                                        filters = {"resolver":self.request.GET["resolver"],
                                                    "machine": self.request.GET["machine"]})
        else:
            week = calendar_objects.Week(int(self.kwargs["year"]), 
                                        int(self.kwargs["month"]), 
                                        int(self.kwargs["week"]), 
                                        calendar_objects.MaintenanceDay,
                                        include=["checks", "jobs"])
        week.get_week_agenda()
        context["week"] = week
        context["mode"] = "maintenance"
        context["form"] = WeekViewFilterForm()
        return context


class maintenanceDayView(TemplateView):
    """DayView Calender.

    uses calender_objects.Day to generate a calender based on the filtered data."""
    

    template_name=os.path.join("planning","day_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(maintenanceDayView, self).get_context_data(*args, **kwargs)
        _filters = {}
        if self.request.GET.get("date", None):
            _day = datetime.datetime.strptime(self.request.GET["date"], "%m/%d/%Y").date()
            if  self.request.GET.get("resolver", None):
                _filters["resolver"]=self.request.GET["resolver"]
            if self.request.GET.get("machine",None):
                _filters["machine"] = self.request.GET["machine"]
                
            _include = get_include(self)
        else:
            _day = datetime.date(int(self.kwargs["year"]),
                                int(self.kwargs["month"]),
                                int(self.kwargs["day"]),
                                )
            _include=["checks", "jobs"]
        
        day = calendar_objects.MaintenanceDay(_day, include=_include,
                                            filters=_filters)
        day.get_agenda()
        context["day"] =day 
        context["mode"] = "maintenance"
        context["form"] = DayViewFilterForm()
        return context


class productionMonthView(TemplateView):
    """MonthView Calender.

    uses calender_objects.Month to generate a calender based on the filtered data."""
    
    template_name=os.path.join("planning","production","month_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionMonthView, self).get_context_data(*args, **kwargs)
        if self.request.GET.get("year", None):
            _month = calendar_objects.Month(int(self.request.GET["year"]),
                                            int(self.request.GET["month"]),
                                            calendar_objects.ProductionDay)
        elif self.kwargs.get("year", None):
            _month = calendar_objects.Month(int(self.kwargs["year"]), 
                                        int(self.kwargs["month"]),
                                        calendar_objects.ProductionDay)
        
        else:
            today =datetime.date.today()
            _month = calendar_objects.Month(today.year, 
                                        today.month,
                                        calendar_objects.ProductionDay)

        _month.get_month_agenda()
        context["month"] = _month
        context["form"] = MonthViewFilterForm()
        return context


class productionWeekView(TemplateView):
    """WEekView Calender.

    uses calender_objects.Week to generate a calender based on the filtered data."""
    
    template_name=os.path.join("planning","production", "week_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionWeekView, self).get_context_data(*args, **kwargs)
        if self.request.GET.get("year", None):
            week = calendar_objects.Week(int(self.request.GET.get("year")),
                                        int(self.request.GET.get("month")),
                                        int(self.request.GET.get("week")),
                                        calendar_objects.ProductionDay)
        else:
            week = calendar_objects.Week(int(self.kwargs["year"]), 
                                        int(self.kwargs["month"]), 
                                        int(self.kwargs["week"]), 
                                        calendar_objects.ProductionDay)
        week.get_week_agenda()
        context["week"] = week
        context["mode"] = "production"
        context["form"] = WeekViewFilterForm()
        return context


class productionDayView(TemplateView):
    """DayView Calender.

    uses calender_objects.Day to generate a calender based on the filtered data."""
    
    template_name=os.path.join("planning","production","day_view.html")

    def get_context_data(self, *args, **kwargs):
        context = super(productionDayView, self).get_context_data(*args, **kwargs)
        if self.request.GET.get("date", None):
            _day = datetime.datetime.strptime(self.request.GET["date"], "%m/%d/%Y")
        else:
            _day = datetime.date(int(self.kwargs["year"]),
                            int(self.kwargs["month"]),
                            int(self.kwargs["day"]))
        day = calendar_objects.ProductionDay(_day)
        day.get_agenda()
        context["day"] =day
        context["mode"] = "production"
        context["form"] = DayViewFilterForm()
        return context