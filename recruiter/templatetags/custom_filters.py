# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def truncate_and_replace(value, truncate_length):
    truncated_value = value[:truncate_length]
    truncated_value = truncated_value.replace('\n', ' ').replace('\s+', ' ')
    # You can perform additional modifications here
    return truncated_value
