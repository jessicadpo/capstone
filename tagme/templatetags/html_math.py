from django import template
register = template.Library()


@register.filter
def subtract(value, arg):
    """Function to do subtraction in HTML Django tags"""
    return value - arg
