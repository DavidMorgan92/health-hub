from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def multiply(value, factor):
    """Multiply a value by a numeric factor."""
    if value is None:
        return 0

    return Decimal(str(value)) * Decimal(str(factor))
