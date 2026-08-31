from django.shortcuts import render

from plans.models import Plan, UserPlanSelection


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'home.html')

    selected_plan_ids = UserPlanSelection.objects.filter(
        user=request.user,
        is_selected=True,
    ).values_list('plan_id', flat=True)

    selected_plans = (
        Plan.objects.filter(pk__in=selected_plan_ids)
        .prefetch_related('events')
        .select_related('product')
    )

    return render(request, 'home.html', {
        'selected_plans': selected_plans,
    })
