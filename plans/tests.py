from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from ecommerce.models import Product
from subscriptions.models import Subscription, SubscriptionPlan
from .models import Plan, PlanEvent, UserPlanSelection
from .templatetags.plan_calendar import _calendar_events


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

    def test_calendar_events_expand_offsets_duration_and_recurrence(self):
        PlanEvent.objects.create(
            plan=self.plan,
            title='Training block',
            instructions='Train.',
            start_offset_days=2,
            duration_days=3,
            recurrence_interval_days=4,
            recurrence_count=2,
        )

        events = _calendar_events([self.plan], date(2026, 8, 31))

        self.assertEqual([event['start'] for event in events], ['2026-09-02', '2026-09-06'])
        self.assertEqual(events[0]['end'], '2026-09-05')

    def test_calendar_events_limit_indefinite_recurrence_to_horizon(self):
        PlanEvent.objects.create(
            plan=self.plan,
            title='Daily walk',
            instructions='Walk.',
            recurrence_interval_days=1,
        )

        events = _calendar_events([self.plan], date(2026, 8, 31))

        self.assertEqual(len(events), 366)
        self.assertEqual(events[-1]['start'], '2027-08-31')

    def test_calendar_events_use_event_titles_and_repeat_plan_colors_by_index(self):
        PlanEvent.objects.create(
            plan=self.plan,
            title='Warm up',
            instructions='Walk.',
        )
        plans = [self.plan]
        for plan_number in range(1, 11):
            product = Product.objects.create(
                name=f'Exercise plan {plan_number}',
                description='A plan',
                product_type=Product.ProductType.EXERCISE_PLAN,
                subscription_price='9.99',
            )
            plan = Plan.objects.create(product=product)
            PlanEvent.objects.create(
                plan=plan,
                title='Warm up',
                instructions='Walk.',
            )
            plans.append(plan)

        events = _calendar_events(plans, date(2026, 8, 31))

        self.assertEqual(events[0]['title'], 'Warm up')
        self.assertEqual(events[0]['color'], events[10]['color'])
        self.assertNotEqual(events[0]['color'], events[1]['color'])

    def test_calendar_events_use_a_plan_activation_date(self):
        PlanEvent.objects.create(
            plan=self.plan,
            title='Warm up',
            instructions='Walk.',
        )
        self.plan.calendar_start_date = date(2026, 9, 4)

        events = _calendar_events([self.plan], date(2026, 8, 31))

        self.assertEqual(events[0]['start'], '2026-09-04')


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

    def test_authenticated_user_sees_plan_calendar_on_home_page(self):
        nutrition_plan_product = Product.objects.create(
            name='Balanced Nutrition',
            description='Nutrition plan',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        nutrition_plan = Plan.objects.create(product=nutrition_plan_product)

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_home_calendar_active',
            stripe_customer_id='cus_home_calendar_active',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_home_calendar_active',
        )
        UserPlanSelection.objects.create(user=self.user, plan=nutrition_plan, is_selected=True)

        self.client.force_login(self.user)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Selected plan calendar')
        self.assertContains(response, 'data-plan-calendar')

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

    def test_plans_home_renders_calendar_even_when_no_plan_is_current(self):
        nutrition_plan_product = Product.objects.create(
            name='Balanced Nutrition',
            description='Nutrition plan',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        nutrition_plan = Plan.objects.create(product=nutrition_plan_product)

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_empty_calendar',
            stripe_customer_id='cus_empty_calendar',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_empty_calendar',
        )

        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Selected plan calendar')
        self.assertContains(response, 'data-plan-calendar')

    def test_inactive_plan_is_never_marked_current(self):
        nutrition_plan_product = Product.objects.create(
            name='Balanced Nutrition',
            description='Nutrition plan',
            product_type=Product.ProductType.NUTRITION_PLAN,
            subscription_price=Decimal('19.99'),
        )
        nutrition_plan = Plan.objects.create(product=nutrition_plan_product)

        inactive_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_inactive_never_current',
            stripe_customer_id='cus_inactive_never_current',
            status=Subscription.Status.CANCELED,
            current_period_end=timezone.now() - timedelta(days=1),
        )
        SubscriptionPlan.objects.create(
            subscription=inactive_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_inactive_never_current',
        )

        UserPlanSelection.objects.create(user=self.user, plan=nutrition_plan, is_selected=True)

        self.client.force_login(self.user)

        response = self.client.get('/plans/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'disabled')
        self.assertNotContains(response, 'checked', html=False)
        self.assertFalse(UserPlanSelection.objects.get(user=self.user, plan=nutrition_plan).is_selected)

    def test_user_can_persist_current_plan_selection_from_plans_home(self):
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

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_selection_active',
            stripe_customer_id='cus_selection_active',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=nutrition_plan,
            stripe_subscription_item_id='si_selection_nutrition',
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=exercise_plan,
            stripe_subscription_item_id='si_selection_exercise',
        )

        self.client.force_login(self.user)

        response = self.client.post('/plans/', {'selected_plans': [str(exercise_plan.pk)]})

        self.assertEqual(response.status_code, 302)
        selection = UserPlanSelection.objects.get(user=self.user, plan=exercise_plan)
        self.assertTrue(selection.is_selected)
        self.assertIsNotNone(selection.activated_at)
        activated_at = selection.activated_at
        self.assertFalse(UserPlanSelection.objects.filter(user=self.user, plan=nutrition_plan, is_selected=True).exists())

        response = self.client.get('/plans/')
        self.assertContains(response, 'checked')
        self.assertContains(response, 'data-plan-calendar')
        self.assertContains(response, 'data-plan-reset-modal')
        self.assertContains(response, 'This will reset the plan schedule.')
        self.assertNotContains(response, 'window.confirm')

        self.client.post('/plans/', {'selected_plans': [str(exercise_plan.pk)]})
        selection.refresh_from_db()
        self.assertEqual(selection.activated_at, activated_at)

        self.client.post('/plans/', {})
        selection.refresh_from_db()
        self.assertFalse(selection.is_selected)
        self.assertIsNone(selection.activated_at)

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
        self.assertContains(response, 'data-plan-calendar')

    def test_plan_detail_lists_distinct_recommended_products(self):
        plan_product = Product.objects.create(
            name='Performance Plan',
            description='Performance plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('29.99'),
        )
        plan = Plan.objects.create(product=plan_product)

        active_subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_detail_recommended',
            stripe_customer_id='cus_detail_recommended',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=active_subscription,
            plan=plan,
            stripe_subscription_item_id='si_detail_recommended',
        )

        protein = Product.objects.create(
            name='Protein Blend Powder',
            description='Protein powder',
            product_type=Product.ProductType.NUTRITION_PRODUCT,
            price=Decimal('24.99'),
            stock=10,
        )
        mat = Product.objects.create(
            name='Yoga Mat Pro',
            description='Exercise mat',
            product_type=Product.ProductType.EXERCISE_PRODUCT,
            price=Decimal('39.99'),
            stock=7,
        )
        bands = Product.objects.create(
            name='Resistance Bands Set',
            description='Bands set',
            product_type=Product.ProductType.EXERCISE_PRODUCT,
            price=Decimal('19.99'),
            stock=5,
        )

        first_event = PlanEvent.objects.create(
            plan=plan,
            title='Strength workout',
            instructions='Lift weights',
            start_offset_days=1,
            duration_days=1,
        )
        first_event.linked_products.set([protein, mat, protein])

        second_event = PlanEvent.objects.create(
            plan=plan,
            title='Mobility workout',
            instructions='Stretch',
            start_offset_days=2,
            duration_days=1,
        )
        second_event.linked_products.set([mat, bands])

        self.client.force_login(self.user)

        response = self.client.get(f'/plans/{plan.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recommended products')
        self.assertContains(response, 'Protein Blend Powder')
        self.assertContains(response, 'Yoga Mat Pro')
        self.assertContains(response, 'Resistance Bands Set')
        self.assertContains(response, 'class="row flex-nowrap overflow-auto g-3 pb-2"')

    def test_plan_detail_hides_calendar_without_active_subscription(self):
        plan_product = Product.objects.create(
            name='Inactive Plan',
            description='An inactive plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('19.99'),
        )
        plan = Plan.objects.create(product=plan_product)
        subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_detail_canceled',
            stripe_customer_id='cus_detail_canceled',
            status=Subscription.Status.CANCELED,
            current_period_end=timezone.now() - timedelta(days=1),
        )
        SubscriptionPlan.objects.create(
            subscription=subscription,
            plan=plan,
            stripe_subscription_item_id='si_detail_canceled',
        )

        self.client.force_login(self.user)

        response = self.client.get(f'/plans/{plan.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You must re-activate a subscription to regain access to this plan.',
        )
        self.assertNotContains(response, 'data-plan-calendar')
