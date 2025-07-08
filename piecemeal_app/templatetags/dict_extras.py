from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return []
    return dictionary.get(key)


@register.filter
def exclude_saved(value):
    if not value:
        return []
    return [d for d in value if d != "saved"]
