import uuid
from datetime import timedelta

from django import template
from django.utils import timezone


register = template.Library()

CALENDAR_HORIZON_DAYS = 365
PLAN_COLORS = (
    '#2563eb',
    '#dc2626',
    '#16a34a',
    '#ca8a04',
    '#9333ea',
    '#0891b2',
    '#ea580c',
    '#4f46e5',
    '#be123c',
    '#15803d',
)


def _as_date(value):
    if value is None:
        return timezone.localdate()
    if hasattr(value, 'date'):
        return value.date()
    return value


def _calendar_events(plans, start_date):
    start_date = _as_date(start_date)
    horizon = start_date + timedelta(days=CALENDAR_HORIZON_DAYS)
    if hasattr(plans, 'events'):
        plans = [plans]
    events = []

    for plan_index, plan in enumerate(plans):
        plan_name = plan.product.name
        plan_color = PLAN_COLORS[plan_index % len(PLAN_COLORS)]
        for plan_event in plan.events.all():
            occurrence_number = 0
            while True:
                occurrence_start = start_date + timedelta(
                    days=plan_event.start_offset_days
                    + occurrence_number * (plan_event.recurrence_interval_days or 0),
                )
                if occurrence_start > horizon:
                    break
                if plan_event.recurrence_count is not None and occurrence_number >= plan_event.recurrence_count:
                    break

                occurrence_end = occurrence_start + timedelta(days=plan_event.duration_days)
                events.append({
                    'id': f'{plan.id}-{plan_event.id}-{occurrence_number}',
                    'title': plan_event.title,
                    'start': occurrence_start.isoformat(),
                    'end': occurrence_end.isoformat(),
                    'allDay': True,
                    'color': plan_color,
                    'extendedProps': {
                        'instructions': plan_event.instructions,
                        'plan': plan_name,
                    },
                })

                if not plan_event.is_recurring:
                    break
                occurrence_number += 1

    return events


@register.inclusion_tag('plans/plan_calendar.html')
def plan_calendar(plans, start_date=None):
    return {
        'calendar_id': f'plan-calendar-{uuid.uuid4().hex}',
        'events_id': f'plan-calendar-events-{uuid.uuid4().hex}',
        'events': _calendar_events(plans, start_date),
    }
