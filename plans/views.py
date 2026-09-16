import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ecommerce.models import Product
from plans.models import Plan, PlanEvent, UserPlanSelection
from subscriptions.models import SubscriptionPlan
from .forms import PlanEventForm, PlanProductForm


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
    all_user_plans = []

    for subscription_plan in subscription_plans:
        product_type = subscription_plan.plan.product.product_type
        if product_type not in grouped_plans:
            continue

        plan = subscription_plan.plan
        all_user_plans.append(plan)
        grouped_plans[product_type].setdefault(plan.id, {
            'plan': plan,
            'subscriptions': [],
        })
        grouped_plans[product_type][plan.id]['subscriptions'].append(subscription_plan.subscription)

    plan_status_by_id = {}
    for product_type, plans_by_id in grouped_plans.items():
        for plan_data in plans_by_id.values():
            plan = plan_data['plan']
            status_data = _plan_status_from_subscriptions(plan_data['subscriptions'])
            plan_status_by_id[plan.id] = status_data['status']

    if request.method == 'POST':
        selected_plan_ids = {int(value) for value in request.POST.getlist('selected_plans') if value}
        activation_time = timezone.now()
        with transaction.atomic():
            for plan in all_user_plans:
                is_active = plan_status_by_id.get(plan.id, 'inactive') == 'active'
                selection, _ = UserPlanSelection.objects.get_or_create(
                    user=request.user,
                    plan=plan,
                )
                should_be_selected = is_active and plan.id in selected_plan_ids
                update_fields = ['is_selected', 'activated_at']
                if should_be_selected and not selection.is_selected:
                    selection.activated_at = activation_time
                elif not should_be_selected:
                    selection.activated_at = None
                selection.is_selected = should_be_selected
                selection.save(update_fields=update_fields)

        messages.success(request, 'Your plan selections were updated.')
        return redirect('plans:plans_home')

    selection_map = {
        selection.plan_id: selection.is_selected
        for selection in UserPlanSelection.objects.filter(
            user=request.user,
            plan_id__in=[plan.id for plan in all_user_plans],
        )
    }
    for plan_id, is_selected in list(selection_map.items()):
        if plan_status_by_id.get(plan_id, 'inactive') != 'active' and is_selected:
            UserPlanSelection.objects.filter(user=request.user, plan_id=plan_id).update(
                is_selected=False,
                activated_at=None,
            )
            selection_map[plan_id] = False

    plan_sections = []
    selected_plan_ids = set()
    for product_type, plans_by_id in grouped_plans.items():
        plans = []
        for plan_data in plans_by_id.values():
            plan = plan_data['plan']
            status_data = _plan_status_from_subscriptions(plan_data['subscriptions'])
            is_active = status_data['status'] == 'active'
            is_selected = is_active and selection_map.get(plan.id, False)
            if is_selected:
                selected_plan_ids.add(plan.id)
            plans.append({
                'plan': plan,
                'status': status_data['status'],
                'status_label': status_data['status_label'],
                'badge_class': status_data['badge_class'],
                'is_selected': is_selected,
                'is_active': is_active,
            })

        plan_sections.append({
            'title': 'Nutrition plans' if product_type == Product.ProductType.NUTRITION_PLAN else 'Exercise plans',
            'plans': sorted(plans, key=lambda item: item['plan'].product.name),
        })

    selected_plans = list(
        Plan.objects.filter(pk__in=selected_plan_ids)
        .prefetch_related('events')
        .select_related('product')
    )
    activation_times = {
        selection.plan_id: selection.activated_at
        for selection in UserPlanSelection.objects.filter(
            user=request.user,
            plan_id__in=selected_plan_ids,
            is_selected=True,
        )
    }
    for plan in selected_plans:
        plan.calendar_start_date = activation_times.get(plan.id)

    return render(request, 'plans/home.html', {
        'plan_sections': plan_sections,
        'selected_plans': selected_plans,
    })


@staff_member_required
def create_plan(request):
    form = PlanProductForm(request.POST or None, request.FILES or None)
    event_data = [{
        'title': '',
        'instructions': '',
        'start_offset_days': 0,
        'duration_days': 1,
        'recurrence_interval_days': None,
        'recurrence_count': None,
    }]
    event_forms = []
    event_error = None

    if request.method == 'POST':
        try:
            event_data = json.loads(request.POST.get('events', '[]'))
        except json.JSONDecodeError:
            event_data = []
            event_error = 'The event data could not be read.'

        if not isinstance(event_data, list):
            event_data = []
            event_error = 'The event data could not be read.'

        for event in event_data:
            event_form = PlanEventForm(event if isinstance(event, dict) else {})
            event_forms.append(event_form)
            if not event_form.is_valid() and event_error is None:
                event_error = 'Check the event details before creating the plan.'

        if not event_data and event_error is None:
            event_error = 'Add at least one event before creating the plan.'

    if (
        request.method == 'POST'
        and form.is_valid()
        and event_error is None
    ):
        with transaction.atomic():
            product = form.save()
            plan = Plan.objects.create(product=product)
            for event_form in event_forms:
                PlanEvent.objects.create(plan=plan, **event_form.cleaned_data)
        messages.success(request, 'Plan created successfully.')
        return redirect('plans:create_plan')

    return render(request, 'plans/create_plan.html', {
        'form': form,
        'event_data': event_data,
        'event_forms': event_forms,
        'event_error': event_error,
    })


@login_required
def detail(request, pk):
    plan = get_object_or_404(
        Plan.objects.select_related('product').prefetch_related(
            'subscriptions__subscription',
            'events__linked_products',
        ),
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

    recommended_products = []
    seen_product_ids = set()
    for event in plan.events.all():
        for product in event.linked_products.all():
            if product.id in seen_product_ids:
                continue
            seen_product_ids.add(product.id)
            recommended_products.append(product)
    recommended_products.sort(key=lambda product: product.name)

    return render(
        request,
        'plans/plan_detail.html',
        {
            'plan': plan,
            'subscriptions': subscriptions,
            'has_plan_access': has_plan_access,
            'recommended_products': recommended_products,
        },
    )
