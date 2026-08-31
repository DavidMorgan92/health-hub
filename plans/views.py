from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ecommerce.models import Product
from subscriptions.models import SubscriptionPlan


def _subscription_badge_class(status):
    badge_classes = {
        'active': 'badge bg-success',
        'past_due': 'badge bg-warning text-dark',
        'canceled': 'badge bg-secondary',
    }
    return badge_classes.get(status, 'badge bg-secondary')


@login_required
def home(request):
    subscription_plans = (
        SubscriptionPlan.objects.filter(subscription__user=request.user)
        .select_related('subscription', 'plan__product')
        .order_by('plan__product__name')
    )

    grouped_plans = {
        Product.ProductType.NUTRITION_PLAN: [],
        Product.ProductType.EXERCISE_PLAN: [],
    }

    for subscription_plan in subscription_plans:
        product_type = subscription_plan.plan.product.product_type
        if product_type not in grouped_plans:
            continue

        grouped_plans[product_type].append({
            'plan': subscription_plan.plan,
            'subscription': subscription_plan.subscription,
            'status': subscription_plan.subscription.status,
            'status_label': subscription_plan.subscription.get_status_display(),
            'badge_class': _subscription_badge_class(subscription_plan.subscription.status),
        })

    plan_sections = [
        {
            'title': 'Nutrition plans',
            'plans': grouped_plans[Product.ProductType.NUTRITION_PLAN],
        },
        {
            'title': 'Exercise plans',
            'plans': grouped_plans[Product.ProductType.EXERCISE_PLAN],
        },
    ]

    return render(request, 'plans/home.html', {'plan_sections': plan_sections})
