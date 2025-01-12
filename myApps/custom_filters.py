from django import template

register = template.Library()

@register.filter
def range_filter(start, end):
    """Generate a range list for use in templates."""
    return range(start, end + 1)
