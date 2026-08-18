from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def multiply(value, factor):
    """Multiply a value by a numeric factor."""
    if value is None:
        return 0

    return Decimal(str(value)) * Decimal(str(factor))


@register.simple_tag
def active_nav(request, url_name):
    """Return the Bootstrap active class when the request matches the target URL name."""
    if not request or not getattr(request, 'resolver_match', None):
        return ''

    current_name = request.resolver_match.url_name
    if current_name == url_name or current_name == url_name.split(':')[-1]:
        return 'active'

    return ''
