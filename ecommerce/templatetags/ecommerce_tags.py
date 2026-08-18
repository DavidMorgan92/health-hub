from decimal import Decimal, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter
def multiply(value, factor):
    """Multiply a value by a numeric factor and round to 2 decimal places."""
    if value is None:
        return 0

    total = Decimal(str(value)) * Decimal(str(factor))
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@register.filter
def money(value):
    """Format a price value as GBP with 2 decimal places."""
    if value is None:
        return '£0.00'

    amount = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f'£{amount:,.2f}'


@register.simple_tag
def active_nav(request, url_name):
    """Return the Bootstrap active class when the request matches the target URL name."""
    if not request or not getattr(request, 'resolver_match', None):
        return ''

    current_name = request.resolver_match.url_name
    if current_name == url_name or current_name == url_name.split(':')[-1]:
        return 'active'

    return ''
