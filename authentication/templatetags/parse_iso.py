from django import template
import datetime

register = template.Library()

@register.filter(expects_localtime=True)
def parse_iso(value):
    if not value:
        return ""
    
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return value
