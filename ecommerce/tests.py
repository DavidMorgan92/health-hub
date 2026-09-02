from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.test import override_settings
from unittest.mock import patch

from .models import Order, Product


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

    def test_cart_displays_total_for_all_items(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(self.product.id): 2, str(plan.id): 1}
        session.save()

        response = self.client.get('/store/cart/')

        self.assertContains(response, 'Cart total')
        self.assertContains(response, '£44.99')

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

        self.assertContains(response, 'class="input-group input-group-sm flex-nowrap"', html=False)
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

    def test_basket_can_be_emptied(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.post('/store/cart/empty/')

        self.assertEqual(response.json(), {'count': 0})
        self.assertEqual(self.client.session['cart'], {})

    def test_cart_shows_empty_basket_button_when_items_exist(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/cart/')

        self.assertContains(response, 'data-empty-cart', html=False)
        self.assertContains(response, 'Empty basket')

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

    def test_checkout_page_lists_cart_items(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/checkout/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pay securely with Stripe')
        self.assertContains(response, 'Resistance Band')
        self.assertContains(response, 'Checkout total')
        self.assertContains(response, '£12.50')

    def test_product_checkout_requires_delivery_address(self):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.get('/store/checkout/')

        self.assertContains(response, 'name="delivery_address"', html=False)
        self.assertContains(response, 'id="delivery-address"', html=False)
        self.assertContains(
            response,
            '<script src="/static/ecommerce/checkout.js?v=1"></script>',
            html=False,
        )
        self.assertContains(response, 'Pay securely with Stripe')
        self.assertContains(response, 'disabled', html=False)

    def test_plan_only_checkout_does_not_require_delivery_address(self):
        user = get_user_model().objects.create_user(
            username='plan-only-buyer',
            password='test-password',
        )
        self.client.force_login(user)
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.get('/store/checkout/')

        self.assertNotContains(response, 'name="delivery_address"', html=False)
        self.assertNotContains(response, 'disabled', html=False)

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.create')
    def test_product_checkout_rejects_missing_delivery_address(self, create_session):
        self.client.post(f'/store/cart/add/{self.product.id}/')

        response = self.client.post('/store/checkout/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a delivery address before continuing to Stripe.')
        create_session.assert_not_called()

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.create')
    def test_product_checkout_persists_order_delivery_address(self, create_session):
        self.client.post(f'/store/cart/add/{self.product.id}/')
        create_session.return_value.url = 'https://checkout.stripe.com/session'
        create_session.return_value.id = 'cs_order_example'

        self.client.post(
            '/store/checkout/',
            {'delivery_address': '12 Health Street, London, W1A 1AA'},
        )

        order = Order.objects.get(stripe_checkout_session_id='cs_order_example')
        self.assertEqual(order.delivery_address, '12 Health Street, London, W1A 1AA')
        self.assertEqual(order.total, Decimal('12.50'))
        self.assertEqual(order.items.get().product, self.product)

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.create')
    def test_mixed_checkout_order_total_excludes_plan_price(self, create_session):
        user = get_user_model().objects.create_user(
            username='mixed-buyer',
            password='test-password',
        )
        self.client.force_login(user)
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(self.product.id): 1, str(plan.id): 1}
        session.save()
        create_session.return_value.url = 'https://checkout.stripe.com/session'
        create_session.return_value.id = 'cs_mixed_example'

        self.client.post(
            '/store/checkout/',
            {'delivery_address': '12 Health Street, London, W1A 1AA'},
        )

        order = Order.objects.get(stripe_checkout_session_id='cs_mixed_example')
        self.assertEqual(order.total, Decimal('12.50'))
        self.assertEqual(order.items.count(), 1)

    def test_anonymous_plan_checkout_requires_an_account_step(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.get('/store/checkout/')

        self.assertRedirects(response, '/store/checkout/account/')

    def test_checkout_account_step_links_to_auth_and_preserves_checkout(self):
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.get('/store/checkout/account/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['checkout_url'], '/store/checkout/')
        self.assertContains(response, 'href="/accounts/login/?next=')
        self.assertContains(response, 'href="/accounts/signup/?next=')

    def test_authenticated_plan_checkout_can_reach_checkout(self):
        user = get_user_model().objects.create_user(
            username='plan-buyer',
            password='test-password',
        )
        self.client.force_login(user)
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()

        response = self.client.get('/store/checkout/')

        self.assertEqual(response.status_code, 200)

    def test_empty_checkout_message_does_not_leak_into_later_checkout(self):
        response = self.client.get('/store/checkout/')

        self.assertRedirects(response, '/store/cart/', fetch_redirect_response=False)
        cart_response = self.client.get('/store/cart/')
        self.assertContains(cart_response, 'Add an item to your cart before checking out.')

        self.client.post(f'/store/cart/add/{self.product.id}/')
        self.client.get('/store/cart/')
        checkout_response = self.client.get('/store/checkout/')

        self.assertNotContains(
            checkout_response,
            'Add an item to your cart before checking out.',
        )

    def test_checkout_stock_error_uses_bootstrap_danger_class(self):
        session = self.client.session
        session['cart'] = {str(self.product.id): 1}
        session.save()
        self.product.stock = 0
        self.product.save()

        response = self.client.post('/store/checkout/', follow=True)

        self.assertContains(response, 'alert-danger')
        self.assertNotContains(response, 'alert-error')

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.create')
    def test_product_checkout_uses_one_time_payment_mode(self, create_session):
        self.client.post(f'/store/cart/add/{self.product.id}/')
        create_session.return_value.url = 'https://checkout.stripe.com/session'
        create_session.return_value.id = 'cs_test_example'

        response = self.client.post(
            '/store/checkout/',
            {'delivery_address': '12 Health Street, London, W1A 1AA'},
        )

        self.assertRedirects(response, 'https://checkout.stripe.com/session', fetch_redirect_response=False)
        self.assertEqual(create_session.call_args.kwargs['mode'], 'payment')
        self.assertNotIn('recurring', create_session.call_args.kwargs['line_items'][0]['price_data'])

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.create')
    def test_plan_checkout_uses_monthly_subscription_mode(self, create_session):
        user = get_user_model().objects.create_user(
            username='plan-buyer',
            password='test-password',
        )
        self.client.force_login(user)
        plan = Product.objects.create(
            name='Beginner Nutrition Plan',
            description='A four-week nutrition plan.',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        session = self.client.session
        session['cart'] = {str(plan.id): 1}
        session.save()
        create_session.return_value.url = 'https://checkout.stripe.com/session'
        create_session.return_value.id = 'cs_test_example'

        response = self.client.post('/store/checkout/')

        self.assertRedirects(response, 'https://checkout.stripe.com/session', fetch_redirect_response=False)
        self.assertEqual(create_session.call_args.kwargs['mode'], 'subscription')
        self.assertEqual(
            create_session.call_args.kwargs['line_items'][0]['price_data']['recurring'],
            {'interval': 'month'},
        )

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.retrieve')
    def test_successful_checkout_empties_cart(self, retrieve_session):
        self.client.post(f'/store/cart/add/{self.product.id}/')
        session = self.client.session
        session['stripe_checkout_session_id'] = 'cs_test_example'
        session.save()
        retrieve_session.return_value.payment_status = 'paid'

        response = self.client.get('/store/checkout/success/?session_id=cs_test_example')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment complete')
        self.assertEqual(self.client.session['cart'], {})
        retrieve_session.assert_called_once_with('cs_test_example')

    @override_settings(STRIPE_SECRET_KEY='sk_test_example')
    @patch('ecommerce.views.stripe.checkout.Session.retrieve')
    def test_unpaid_checkout_keeps_cart(self, retrieve_session):
        self.client.post(f'/store/cart/add/{self.product.id}/')
        session = self.client.session
        session['stripe_checkout_session_id'] = 'cs_test_example'
        session.save()
        retrieve_session.return_value.payment_status = 'unpaid'

        response = self.client.get('/store/checkout/success/?session_id=cs_test_example')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment cancelled')
        self.assertEqual(self.client.session['cart'], {str(self.product.id): 1})


class CartTemplateFilterTests(SimpleTestCase):
    def test_multiply_filter_multiplies_decimal_and_quantity(self):
        template = Template('{% load ecommerce_tags %}{{ value|multiply:quantity }}')
        rendered = template.render(Context({'value': Decimal('12.50'), 'quantity': 3}))

        self.assertEqual(rendered.strip(), '37.50')

    def test_money_filter_formats_price_as_gbp(self):
        template = Template('{% load ecommerce_tags %}{{ value|money }}')
        rendered = template.render(Context({'value': Decimal('12.50')}))

        self.assertEqual(rendered.strip(), '£12.50')
