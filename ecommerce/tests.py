from decimal import Decimal

from django.template import Context, Template
from django.test import SimpleTestCase


class CartTemplateFilterTests(SimpleTestCase):
    def test_multiply_filter_multiplies_decimal_and_quantity(self):
        template = Template('{% load ecommerce_tags %}{{ value|multiply:quantity }}')
        rendered = template.render(Context({'value': Decimal('12.50'), 'quantity': 3}))

        self.assertEqual(rendered.strip(), '37.50')

    def test_money_filter_formats_price_as_gbp(self):
        template = Template('{% load ecommerce_tags %}{{ value|money }}')
        rendered = template.render(Context({'value': Decimal('12.50')}))

        self.assertEqual(rendered.strip(), '£12.50')
