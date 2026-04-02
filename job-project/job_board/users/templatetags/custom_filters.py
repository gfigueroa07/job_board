from django import template

register = template.Library()

@register.filter
def split(value, key):
    if value:
        return [v.strip() for v in value.split(key) if v.strip()]
    return []