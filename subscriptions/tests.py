from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.test import override_settings
from unittest.mock import patch

from ecommerce.models import Product
from plans.models import Plan
from .models import Subscription, SubscriptionPlan


class SubscriptionAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='subscriber',
            password='test-password',
        )
        product = Product.objects.create(
            name='Exercise plan',
            description='A plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('9.99'),
        )
        self.plan = Plan.objects.create(product=product)
        self.subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_test',
            stripe_customer_id='cus_test',
            checkout_session_id='cs_test',
            status=Subscription.Status.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )
        SubscriptionPlan.objects.create(
            subscription=self.subscription,
            plan=self.plan,
            stripe_subscription_item_id='si_test',
        )

    def test_active_subscription_grants_access(self):
        self.assertTrue(self.subscription.grants_access)

    def test_canceled_subscription_does_not_grant_access(self):
        self.subscription.status = Subscription.Status.CANCELED
        self.subscription.save(update_fields=['status', 'updated_at'])

        self.assertFalse(self.subscription.grants_access)

    def test_expired_subscription_does_not_grant_access(self):
        self.subscription.current_period_end = timezone.now() - timedelta(seconds=1)
        self.subscription.save(update_fields=['current_period_end', 'updated_at'])

        self.assertFalse(self.subscription.grants_access)

    def test_past_due_subscription_does_not_grant_access(self):
        self.subscription.status = Subscription.Status.PAST_DUE
        self.subscription.save(update_fields=['status', 'updated_at'])

        self.assertFalse(self.subscription.grants_access)


class StripeWebhookTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='webhook-user',
            password='test-password',
        )
        product = Product.objects.create(
            name='Exercise plan',
            description='A plan',
            product_type=Product.ProductType.EXERCISE_PLAN,
            subscription_price=Decimal('9.99'),
        )
        self.plan = Plan.objects.create(product=product)

    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_test')
    @patch('subscriptions.views.stripe.Webhook.construct_event')
    def test_subscription_webhook_tracks_plan_access_and_cancellation(self, construct_event):
        period_end = int((timezone.now() + timedelta(days=30)).timestamp())
        construct_event.return_value = {
            'type': 'customer.subscription.created',
            'data': {
                'object': {
                    'id': 'sub_webhook',
                    'customer': 'cus_webhook',
                    'status': 'active',
                    'current_period_start': int(timezone.now().timestamp()),
                    'current_period_end': period_end,
                    'cancel_at_period_end': False,
                    'metadata': {
                        'user_id': str(self.user.id),
                        'plan_product_ids': str(self.plan.product_id),
                    },
                    'items': {'data': [{'id': 'si_webhook'}]},
                },
            },
        }

        response = self.client.post(
            '/subscriptions/stripe/webhook/',
            b'event-payload',
            HTTP_STRIPE_SIGNATURE='signature',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        subscription = Subscription.objects.get(stripe_subscription_id='sub_webhook')
        self.assertTrue(subscription.grants_access)
        self.assertEqual(subscription.stripe_status, 'active')
        self.assertEqual(
            subscription.plans.get().plan_id,
            self.plan.id,
        )

        construct_event.return_value['type'] = 'customer.subscription.deleted'
        construct_event.return_value['data']['object']['status'] = 'canceled'
        self.client.post(
            '/subscriptions/stripe/webhook/',
            b'event-payload',
            HTTP_STRIPE_SIGNATURE='signature',
            content_type='application/json',
        )

        subscription.refresh_from_db()
        self.assertFalse(subscription.grants_access)

    def test_checkout_session_does_not_overwrite_active_subscription(self):
        period_end = timezone.now() + timedelta(days=30)
        subscription = Subscription.objects.create(
            user=self.user,
            stripe_subscription_id='sub_checkout',
            status=Subscription.Status.ACTIVE,
            current_period_end=period_end,
        )

        from .services import record_checkout_session

        record_checkout_session({
            'id': 'cs_checkout',
            'subscription': 'sub_checkout',
            'customer': 'cus_checkout',
            'client_reference_id': str(self.user.id),
        })

        subscription.refresh_from_db()
        self.assertEqual(subscription.status, Subscription.Status.ACTIVE)

