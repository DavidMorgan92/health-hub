from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from ecommerce.models import Product
from plans.models import Plan
from subscriptions.models import SubscriptionPlan


def _subscription_badge_class(status):
    badge_classes = {
        'active': 'badge bg-success',
        'past_due': 'badge bg-warning text-dark',
        'canceled': 'badge bg-secondary',
    }
    return badge_classes.get(status, 'badge bg-secondary')


def _plan_status_from_subscriptions(plan_subscriptions):
    if any(sub.status == 'active' for sub in plan_subscriptions):
        return {
            'status': 'active',
            'status_label': 'Active',
            'badge_class': 'badge bg-success',
        }

    return {
        'status': 'inactive',
        'status_label': 'Inactive',
        'badge_class': 'badge bg-secondary',
    }


@login_required
def home(request):
    subscription_plans = (
        SubscriptionPlan.objects.filter(subscription__user=request.user)
        .select_related('subscription', 'plan__product')
        .order_by('plan__product__name')
    )

    grouped_plans = {
        Product.ProductType.NUTRITION_PLAN: {},
        Product.ProductType.EXERCISE_PLAN: {},
    }

    for subscription_plan in subscription_plans:
        product_type = subscription_plan.plan.product.product_type
        if product_type not in grouped_plans:
            continue

        plan = subscription_plan.plan
        grouped_plans[product_type].setdefault(plan.id, {
            'plan': plan,
            'subscriptions': [],
        })
        grouped_plans[product_type][plan.id]['subscriptions'].append(subscription_plan.subscription)

    plan_sections = []
    for product_type, plans_by_id in grouped_plans.items():
        plans = []
        for plan_data in plans_by_id.values():
            status_data = _plan_status_from_subscriptions(plan_data['subscriptions'])
            plans.append({
                'plan': plan_data['plan'],
                'status': status_data['status'],
                'status_label': status_data['status_label'],
                'badge_class': status_data['badge_class'],
            })

        plan_sections.append({
            'title': 'Nutrition plans' if product_type == Product.ProductType.NUTRITION_PLAN else 'Exercise plans',
            'plans': sorted(plans, key=lambda item: item['plan'].product.name),
        })

    return render(request, 'plans/home.html', {'plan_sections': plan_sections})


@login_required
def detail(request, pk):
    plan = get_object_or_404(
        Plan.objects.select_related('product').prefetch_related('subscriptions__subscription'),
        pk=pk,
    )

    user_subscription_plans = plan.subscriptions.filter(subscription__user=request.user)
    subscriptions = []
    has_plan_access = False
    for subscription_plan in user_subscription_plans.select_related('subscription'):
        subscription = subscription_plan.subscription
        has_plan_access = has_plan_access or subscription.grants_access
        subscriptions.append({
            'subscription': subscription,
            'status': subscription.status,
            'status_label': subscription.get_status_display(),
            'badge_class': _subscription_badge_class(subscription.status),
        })

    return render(
        request,
        'plans/plan_detail.html',
        {
            'plan': plan,
            'subscriptions': subscriptions,
            'has_plan_access': has_plan_access,
        },
    )
