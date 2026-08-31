from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from ecommerce.models import Product
from subscriptions.models import Subscription, SubscriptionPlan
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


class SeedPlansCommandTests(TestCase):
    def test_seed_creates_a_plan_for_every_seeded_plan_product(self):
        call_command('seed_products')

        call_command('seed_plans')

        plan_products = Product.objects.filter(
            product_type__in=[
                Product.ProductType.NUTRITION_PLAN,
                Product.ProductType.EXERCISE_PLAN,
            ],
        )
        self.assertEqual(Plan.objects.count(), plan_products.count())
        self.assertEqual(PlanEvent.objects.count(), 60)
        self.assertGreater(
            PlanEvent.objects.filter(linked_products__isnull=False).distinct().count(),
            0,
        )

    def test_seed_is_idempotent(self):
        call_command('seed_products')
        call_command('seed_plans')

        call_command('seed_plans')

        self.assertEqual(Plan.objects.count(), 20)
        self.assertEqual(PlanEvent.objects.count(), 60)


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

    def test_authenticated_user_sees_unique_grouped_plans_with_active_status_priority(self):
        other_user = get_user_model().objects.create_user(
            username='other-plan-user',
            password='test-password',
        )

        nutrition_plan_product = Product.objects.create(
            name='Balanced Nutrition',
            description='Nutrition plan',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        nutrition_plan = Plan.objects.create(product=nutrition_plan_product)

        exercise_plan_product = Product.objects.create(
            name='Strength Builder',
            description='Exercise plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('29.99'),
        )
        exercise_plan = Plan.objects.create(product=exercise_plan_product)

        inactive_plan_product = Product.objects.create(
            name='Inactive Recovery',
            description='An inactive exercise plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('15.99'),
        )
        inactive_plan = Plan.objects.create(product=inactive_plan_product)

        other_exercise_plan_product = Product.objects.create(
            name='Other Exercise',
            description='Another exercise plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('12.99'),
        )
        other_exercise_plan = Plan.objects.create(product=other_exercise_plan_product)

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_active',
            stripe_customer_id='cus_active',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_active_nutrition',
        )

        past_due_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_past_due',
            stripe_customer_id='cus_past_due',
            status=Subscription.Status.PAST_DUE,
            current_period_end=timezone.now() + timedelta(days=7),
        )
        SubscriptionPlan.objects.create(
            subscription=past_due_subscription,
            plan=exercise_plan,
            stripe_subscription_item_id='si_past_due_exercise',
        )

        inactive_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_canceled',
            stripe_customer_id='cus_canceled',
            status=Subscription.Status.CANCELED,
            current_period_end=timezone.now() - timedelta(days=1),
        )
        SubscriptionPlan.objects.create(
            subscription=inactive_subscription,
            plan=exercise_plan,
            stripe_subscription_item_id='si_canceled_exercise',
        )

        canceled_only_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_inactive_only',
            stripe_customer_id='cus_inactive_only',
            status=Subscription.Status.CANCELED,
            current_period_end=timezone.now() - timedelta(days=5),
        )
        SubscriptionPlan.objects.create(
            subscription=canceled_only_subscription,
            plan=inactive_plan,
            stripe_subscription_item_id='si_inactive_only',
        )

        active_subscription_for_same_plan = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_active_same_plan',
            stripe_customer_id='cus_active_same_plan',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription_for_same_plan,
            plan=exercise_plan,
            stripe_subscription_item_id='si_active_same_plan',
        )

        other_subscription = Subscription.objects.create(
            user=other_user,
            stripe_subscription_id='sub_other',
            stripe_customer_id='cus_other',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=other_subscription,
            plan=other_exercise_plan,
            stripe_subscription_item_id='si_other_exercise',
        )

        self.client.force_login(self.user)

        response = self.client.get('/plans/')
        response_html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nutrition plans')
        self.assertContains(response, 'Exercise plans')
        self.assertContains(response, 'Balanced Nutrition')
        self.assertContains(response, 'Strength Builder')
        self.assertContains(response, 'Inactive Recovery')
        self.assertContains(response, 'Active')
        self.assertContains(response, 'Inactive')
        self.assertContains(response, 'class="badge bg-success"')
        self.assertContains(response, 'class="badge bg-secondary"')
        self.assertEqual(response_html.count('Strength Builder'), 1)
        self.assertNotContains(response, 'Other Exercise')

    def test_authenticated_user_can_view_plan_detail_with_subscription_statuses(self):
        nutrition_plan_product = Product.objects.create(
            name='Balanced Nutrition',
            description='Nutrition plan',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        nutrition_plan = Plan.objects.create(product=nutrition_plan_product)

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_detail_active',
            stripe_customer_id='cus_detail_active',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_detail_active',
        )

        past_due_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_detail_past_due',
            stripe_customer_id='cus_detail_past_due',
            status=Subscription.Status.PAST_DUE,
            current_period_end=timezone.now() + timedelta(days=5),
        )
        SubscriptionPlan.objects.create(
            subscription=past_due_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_detail_past_due',
        )

        other_user = get_user_model().objects.create_user(
            username='other-detail-plan-user',
            password='test-password',
        )
        other_subscription = Subscription.objects.create(
            user=other_user,
            stripe_subscription_id='sub_detail_other',
            stripe_customer_id='cus_detail_other',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=other_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_detail_other',
        )

        self.client.force_login(self.user)

        response = self.client.get(f'/plans/{nutrition_plan.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Balanced Nutrition')
        self.assertContains(response, 'Subscriptions')
        self.assertContains(response, 'sub_detail_active')
        self.assertContains(response, 'sub_detail_past_due')
        self.assertNotContains(response, 'sub_detail_other')
        self.assertContains(response, 'class="badge bg-success"')
        self.assertContains(response, 'class="badge bg-warning text-dark"')
