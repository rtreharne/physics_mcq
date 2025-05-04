from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, '')

@register.filter
def percent(value, total):
    try:
        value = float(value)
        total = float(total)
        if total <= 0:
            return "–"
        return f"{(value / total) * 100:.1f}%"
    except (ValueError, ZeroDivisionError, TypeError):
        return "–"
