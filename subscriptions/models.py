from django.conf import settings
from django.db import models
from django.utils import timezone

from plans.models import Plan


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past due'
        CANCELED = 'canceled', 'Canceled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='subscriptions',
    )
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    checkout_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CANCELED,
    )
    stripe_status = models.CharField(
        max_length=30,
        blank=True,
        help_text='The last status reported by Stripe.',
    )
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def grants_access(self):
        return (
            self.status == self.Status.ACTIVE
            and self.current_period_end is not None
            and self.current_period_end > timezone.now()
        )

    def __str__(self):
        return f'{self.user} - {self.stripe_subscription_id}'


class SubscriptionPlan(models.Model):
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='plans',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
    )
    stripe_subscription_item_id = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'plan'],
                name='unique_subscription_plan',
            ),
        ]

    def __str__(self):
        return f'{self.subscription} - {self.plan}'
