from django import template

register = template.Library()

@register.filter
def commaise(value):
    try:
        value = int(value)
    except:
        return value
    if abs(value) < 1000:
        return str(value)
    else:
        if value < 0:
            value *= -1
            return '-' + commaise(value/1000) + ',' + str(value % 1000).rjust(3, '0')
        else:
            return commaise(value/1000) + ',' + str(value % 1000).rjust(3, '0')