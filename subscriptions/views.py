import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ecommerce.models import Order
from .services import record_checkout_session, sync_stripe_subscription


@csrf_exempt
def stripe_webhook(request):
    if request.method != 'POST' or not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=400)

    signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    event_type = event['type']
    event_data = event['data']['object']
    if event_type == 'checkout.session.completed':
        Order.objects.filter(
            stripe_checkout_session_id=event_data.get('id'),
        ).update(status=Order.Status.PAID)
        record_checkout_session(event_data)
    elif event_type in {
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
    }:
        sync_stripe_subscription(event_data)

    return HttpResponse(status=200)
