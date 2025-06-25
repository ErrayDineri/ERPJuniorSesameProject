from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def abs(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0
