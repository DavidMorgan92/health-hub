from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ecommerce.models import Product
from .models import Plan, PlanEvent


class PlanModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name='Exercise plan',
            description='A plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price='9.99',
        )
        self.plan = Plan.objects.create(product=self.product)

    def test_event_can_be_one_off_at_a_relative_offset(self):
        event = PlanEvent(
            plan=self.plan,
            title='Warm up',
            instructions='Walk for ten minutes.',
            start_offset_days=3,
        )

        event.full_clean()

        self.assertFalse(event.is_recurring)

    def test_event_can_repeat_a_fixed_number_of_times(self):
        event = PlanEvent(
            plan=self.plan,
            title='Strength session',
            instructions='Complete the circuit.',
            recurrence_interval_days=7,
            recurrence_count=4,
        )

        event.full_clean()

        self.assertTrue(event.is_recurring)
        self.assertFalse(event.repeats_indefinitely)

    def test_event_can_repeat_indefinitely(self):
        event = PlanEvent(
            plan=self.plan,
            title='Daily walk',
            instructions='Walk for thirty minutes.',
            recurrence_interval_days=1,
        )

        event.full_clean()

        self.assertTrue(event.repeats_indefinitely)

    def test_repeat_count_requires_an_interval(self):
        event = PlanEvent(
            plan=self.plan,
            title='Session',
            instructions='Complete the session.',
            recurrence_count=2,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_plan_requires_a_plan_product(self):
        product = Product.objects.create(
            name='Resistance band',
            description='A product',
            product_type=Product.ProductType.EXERCISE_PRODUCT,
            price='12.00',
        )

        with self.assertRaises(ValidationError):
            Plan(product=product).full_clean()


class PlansHomeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='plan-user',
            password='test-password',
        )

    def test_plans_home_requires_authentication(self):
        response = self.client.get('/plans/')

        self.assertRedirects(response, '/accounts/login/?next=/plans/')

    def test_authenticated_user_can_view_plans_home(self):
        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Plans</h1>', html=False)

    def test_authenticated_user_sees_plans_nav_item(self):
        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertContains(response, 'href="/plans/"')
        self.assertContains(response, 'class="nav-link active"')
