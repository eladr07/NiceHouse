from django import template

register = template.Library()

@register.filter
def commaise(value):
    value = int(value)
    if value < 1000:
        return str(value)
    else:
        return commaise(value/1000) + ',' + str(value % 1000).rjust(3, '0')