from django import template

register = template.Library()


@register.filter
def floatval(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def macro_ratio(macro_grams, total_calories):
    if float(macro_grams) == 0 or float(total_calories) == 0:
        return 0
    return (float(macro_grams) * 4) / float(total_calories)


@register.filter
def fats_ratio(macro_grams, total_calories):
    if macro_grams == 0 or total_calories == 0:
        return 0
    return (macro_grams * 9) / total_calories
