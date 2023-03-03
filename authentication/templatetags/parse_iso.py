from django import template
import datetime

register = template.Library()
@register.filter(expects_localtime=True)
def parse_iso(value):
    return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")