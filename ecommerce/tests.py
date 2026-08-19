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

    def test_store_includes_search_form_for_all_product_types(self):
        response = self.client.get('/store/')

        self.assertContains(response, '<form method="get" action="/store/search/"', html=False)
        self.assertContains(response, 'name="q"', html=False)
        self.assertContains(response, 'value="">All product types', html=False)
        for product_type in Product.ProductType.values:
            self.assertContains(response, f'value="{product_type}"', html=False)


class ProductSearchViewTests(TestCase):
    def setUp(self):
        Product.objects.create(
            name='Meal Planning Basics',
            description='A nutrition plan for balanced meals.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('4.99'),
        )
        Product.objects.create(
            name='Meal Replacement Shake',
            description='A nutrition product for busy days.',
            product_type=Product.ProductType.NUTRITION_PRODUCT,
            price=Decimal('12.50'),
            stock=2,
        )
        Product.objects.create(
            name='Strength Starter',
            description='An exercise plan for beginners.',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('8.99'),
        )

    def test_search_filters_by_query_and_product_type(self):
        response = self.client.get(
            '/store/search/',
            {'q': 'meal', 'product_type': Product.ProductType.NUTRITION_PLAN},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meal Planning Basics')
        self.assertNotContains(response, 'Meal Replacement Shake')
        self.assertNotContains(response, 'Strength Starter')
        self.assertContains(response, 'value="meal"', html=False)
        self.assertContains(response, 'value="nutrition_plan" selected', html=False)

    def test_store_search_form_is_available_on_the_store_page(self):
        response = self.client.get('/store/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form method="get" action="/store/search/"', html=False)
        self.assertContains(response, 'name="product_type"', html=False)

    def test_search_results_are_rendered_as_a_vertical_list(self):
        response = self.client.get('/store/search/', {'q': 'meal'})

        self.assertContains(response, '<div class="row row-cols-1 g-3">', html=False)
        self.assertContains(response, 'Meal Planning Basics')
        self.assertContains(response, 'Meal Replacement Shake')

    def test_store_nav_item_is_active_on_search_results(self):
        response = self.client.get('/store/search/')

        self.assertContains(response, 'class="nav-link active"')
        self.assertContains(response, 'href="/store/" aria-current="page"', html=False)


class CartViewTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Resistance Band',
            description='A durable exercise band.',
            product_type=Product.ProductType.EXERCISE_PRODUCT,
            price=Decimal('12.50'),
            stock=3,
        )

    def test_plan_cart_items_use_subscription_price(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 2}
        session.save()

        response = self.client.get('/store/cart/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '£19.99')
        self.assertContains(response, '£39.98')

    def test_add_to_cart_returns_count_and_keeps_session_data(self):
        response = self.client.post(
            f'/store/cart/add/{self.product.id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 1})
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 1})

    def test_adding_one_off_product_again_increments_count(self):
        url = f'/store/cart/add/{self.product.id}/'

        self.client.post(url)
        response = self.client.post(url)

        self.assertEqual(response.json(), {'count': 2})

    def test_product_quantity_can_be_updated(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.post(
            f'/store/cart/update/{self.product.id}/',
            {'quantity': 2},
        )

        self.assertEqual(response.json(), {'quantity': 2, 'total': '£25.00', 'count': 2})
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 2})

    def test_product_decrease_control_is_disabled_at_quantity_one(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/cart/')

        self.assertRegex(
            response.content.decode(),
            r'data-cart-decrease[\s\S]*aria-label="Decrease Resistance Band quantity"[\s\S]*disabled',
        )

    def test_cart_uses_input_group_controls_for_products(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/cart/')

        self.assertContains(response, 'class="input-group input-group-sm"', html=False)
        self.assertContains(response, 'data-cart-remove', html=False)
        self.assertContains(response, 'aria-label="Delete Resistance Band from cart"', html=False)

    def test_product_quantity_cannot_exceed_stock(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.post(
            f'/store/cart/update/{self.product.id}/',
            {'quantity': 4},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 1})

    def test_product_can_be_removed(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.post(f'/store/cart/remove/{self.product.id}/')

        self.assertEqual(response.json(), {'count': 0})
        self.assertEqual(self.client.session['cart'], {})

    def test_plan_has_remove_control_but_no_quantity_controls(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.get('/store/cart/')

        self.assertNotContains(response, 'data-update-url')
        self.assertContains(response, 'data-remove-url')
        self.assertContains(response, 'data-cart-decrease', html=False)
        self.assertContains(response, 'data-cart-increase', html=False)
        self.assertContains(response, 'aria-label="Delete Beginner Nutrition Plan from cart"', html=False)

    def test_plan_can_be_removed(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.post(f'/store/cart/remove/{plan.id}/')

        self.assertEqual(response.json(), {'count': 0})
        self.assertEqual(self.client.session['cart'], {})

    def test_navbar_badge_uses_current_cart_count(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/search/')

        self.assertContains(response, 'id="cart-count-badge"', html=False)
        self.assertRegex(
            response.content.decode(),
            r'id="cart-count-badge"[^>]*>\s*1\s*</span>',
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
