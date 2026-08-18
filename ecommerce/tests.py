from decimal import Decimal

from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from .models import Product


class ProductTests(TestCase):
    def test_plan_requires_monthly_subscription_price_and_cannot_be_multiplied(self):
        plan = Product(
            name='Beginner Exercise Plan',
            description='A four-week plan.',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('9.99'),
        )

        plan.full_clean()

        self.assertTrue(plan.is_plan)
        self.assertFalse(plan.allows_multiple_purchases)

    def test_one_off_product_requires_one_off_price(self):
        product = Product(
            name='Resistance Band',
            description='A durable exercise band.',
            product_type=Product.ProductType.EXERCISE_PRODUCT,
            price=Decimal('12.50'),
        )

        product.full_clean()

        self.assertFalse(product.is_plan)
        self.assertTrue(product.allows_multiple_purchases)

    def test_plan_cannot_have_one_off_price(self):
        plan = Product(
            name='Nutrition Plan',
            description='A meal plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            price=Decimal('12.50'),
            subscription_price=Decimal('4.99'),
        )

        with self.assertRaises(ValidationError):
            plan.full_clean()


class StoreViewTests(TestCase):
    def test_store_displays_all_four_product_sections(self):
        response = self.client.get('/store/')

        self.assertEqual(response.status_code, 200)
        for section_title in (
            'Nutrition Plans',
            'Exercise Plans',
            'Nutrition Products',
            'Exercise Products',
        ):
            self.assertContains(response, section_title)

    def test_store_limits_each_section_to_five_products(self):
        for product_number in range(6):
            Product.objects.create(
                name=f'Exercise Product {product_number}',
                description='An exercise product.',
                product_type=Product.ProductType.EXERCISE_PRODUCT,
                price=Decimal('10.00'),
                stock=1,
            )

        response = self.client.get('/store/')

        self.assertEqual(response.content.decode().count('Exercise Product '), 5)

    def test_store_links_each_section_to_filtered_search(self):
        response = self.client.get('/store/')

        for product_type in Product.ProductType.values:
            self.assertContains(
                response,
                f'/store/search/?product_type={product_type}',
            )


class CartTemplateFilterTests(SimpleTestCase):
    def test_multiply_filter_multiplies_decimal_and_quantity(self):
        template = Template('{% load ecommerce_tags %}{{ value|multiply:quantity }}')
        rendered = template.render(Context({'value': Decimal('12.50'), 'quantity': 3}))

        self.assertEqual(rendered.strip(), '37.50')

    def test_money_filter_formats_price_as_gbp(self):
        template = Template('{% load ecommerce_tags %}{{ value|money }}')
        rendered = template.render(Context({'value': Decimal('12.50')}))

        self.assertEqual(rendered.strip(), '£12.50')
