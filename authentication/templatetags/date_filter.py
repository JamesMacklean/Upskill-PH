from django import template

register = template.Library()

@register.filter
def is_valid_date(date_str):
    """
    Check if a date string is not None, empty, or '0000-00-00 00:00:00'
    """
    if not date_str or date_str in ["", "0000-00-00 00:00:00"]:
        return False
    return True
