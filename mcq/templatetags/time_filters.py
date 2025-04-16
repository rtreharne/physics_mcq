from django import template

register = template.Library()

@register.filter
def seconds_to_minutes(seconds):
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    except (ValueError, TypeError):
        return "–"
