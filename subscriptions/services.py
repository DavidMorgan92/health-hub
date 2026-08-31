from datetime import datetime, timezone as datetime_timezone

from django.db import transaction

from plans.models import Plan
from .models import Subscription, SubscriptionPlan


def _normalise_status(stripe_status):
    if stripe_status in {'active', 'trialing'}:
        return Subscription.Status.ACTIVE
    if stripe_status == 'past_due':
        return Subscription.Status.PAST_DUE
    return Subscription.Status.CANCELED


def _stripe_datetime(timestamp):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=datetime_timezone.utc)


def _plan_product_ids(metadata):
    return [
        int(product_id)
        for product_id in metadata.get('plan_product_ids', '').split(',')
        if product_id
    ]


@transaction.atomic
def record_checkout_session(session):
    subscription_id = session.get('subscription')
    user_id = session.get('client_reference_id') or session.get('metadata', {}).get('user_id')
    if not subscription_id or not user_id:
        return None

    subscription, _ = Subscription.objects.update_or_create(
        stripe_subscription_id=subscription_id,
        defaults={
            'user_id': user_id,
            'stripe_customer_id': session.get('customer', ''),
            'checkout_session_id': session.get('id'),
        },
    )
    return subscription


@transaction.atomic
def sync_stripe_subscription(stripe_subscription):
    subscription_id = stripe_subscription['id']
    metadata = stripe_subscription.get('metadata', {})
    subscription = Subscription.objects.filter(
        stripe_subscription_id=subscription_id,
    ).first()

    user_id = metadata.get('user_id')
    if subscription is None and not user_id:
        raise ValueError('Stripe subscription has no associated user.')

    defaults = {
        'status': _normalise_status(stripe_subscription.get('status')),
        'stripe_status': stripe_subscription.get('status', ''),
        'stripe_customer_id': stripe_subscription.get('customer', ''),
        'current_period_start': _stripe_datetime(stripe_subscription.get('current_period_start')),
        'current_period_end': _stripe_datetime(stripe_subscription.get('current_period_end')),
        'cancel_at_period_end': stripe_subscription.get('cancel_at_period_end', False),
        'canceled_at': _stripe_datetime(stripe_subscription.get('canceled_at')),
    }
    if subscription is None:
        defaults['user_id'] = user_id
        subscription = Subscription.objects.create(
            stripe_subscription_id=subscription_id,
            **defaults,
        )
    else:
        for field, value in defaults.items():
            setattr(subscription, field, value)
        subscription.save()

    product_ids = _plan_product_ids(metadata)
    if product_ids:
        plans_by_product_id = {
            plan.product_id: plan
            for plan in Plan.objects.filter(product_id__in=product_ids)
        }
        SubscriptionPlan.objects.filter(subscription=subscription).delete()
        for item, product_id in zip(
            stripe_subscription.get('items', {}).get('data', []),
            product_ids,
        ):
            plan = plans_by_product_id.get(product_id)
            if plan and item.get('id'):
                SubscriptionPlan.objects.create(
                    subscription=subscription,
                    plan=plan,
                    stripe_subscription_item_id=item['id'],
                )

    return subscription
