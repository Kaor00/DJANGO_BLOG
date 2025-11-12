from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Умножает value на arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return ''