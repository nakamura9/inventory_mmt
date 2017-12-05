from django import template

register = template.Library()

@register.filter
def safer_id(id):
    return "-".join(id.split(" "))
