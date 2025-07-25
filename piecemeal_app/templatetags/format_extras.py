from django import template

register = template.Library()


@register.filter
def smart_float(value):
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    if abs(num - round(num)) < 0.01:
        return f"{int(round(num))}"
    return f"{num:.1f}"


@register.filter
def smart_int(value):
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    return f"{int(round(num))}"
