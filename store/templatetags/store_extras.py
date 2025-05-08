# store/templatetags/store_extras.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Allows dictionary lookup in templates using a variable key."""
    return dictionary.get(key)
