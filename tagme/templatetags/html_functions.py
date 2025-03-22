"""Module for implementing functions in HTML Django tags"""
from django import template
register = template.Library()


@register.filter
def subtract(value, arg):
    """Function to do subtraction in HTML Django tags"""
    return int(value) - int(arg)


@register.filter
def url_contains_pinned_items(request):
    """Function to check if request.get_full_path is "/pinned-items/{{request.user.username}}"""
    if f"/pinned-items/{request.user.username}" in request.get_full_path():
        return True
    return False


@register.filter
def tag_item_count_dict_to_string(tag_count_dict):
    """Function to convert a {'tag': 'tag_value', 'item_count': integer} dict into a "tag_value (integer)" string"""
    if isinstance(tag_count_dict, dict):
        return f"{tag_count_dict['tag']} ({tag_count_dict['item_count']})"
    return ""
