from django.core.exceptions import ValidationError
from django.db import models

from ecommerce.models import Product


class Plan(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='plan',
        limit_choices_to={
            'product_type__in': [
                Product.ProductType.NUTRITION_PLAN,
                Product.ProductType.EXERCISE_PLAN,
            ],
        },
    )

    def clean(self):
        super().clean()
        if self.product and not self.product.is_plan:
            raise ValidationError({'product': 'A plan must use a plan product type.'})

    def __str__(self):
        return self.product.name


class PlanEvent(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    start_offset_days = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField(default=1)
    recurrence_interval_days = models.PositiveIntegerField(null=True, blank=True)
    recurrence_count = models.PositiveIntegerField(null=True, blank=True)
    linked_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='plan_events',
    )

    def clean(self):
        super().clean()
        if self.duration_days < 1:
            raise ValidationError({'duration_days': 'Duration must be at least one day.'})

        is_recurring = self.recurrence_interval_days is not None
        has_repeat_count = self.recurrence_count is not None

        if has_repeat_count and not is_recurring:
            raise ValidationError({
                'recurrence_count': 'A repeat count requires a recurrence interval.',
            })
        if is_recurring and self.recurrence_interval_days < 1:
            raise ValidationError({
                'recurrence_interval_days': 'Recurrence interval must be at least one day.',
            })
        if has_repeat_count and self.recurrence_count < 1:
            raise ValidationError({
                'recurrence_count': 'Repeat count must be at least one.',
            })

    @property
    def is_recurring(self):
        return self.recurrence_interval_days is not None

    @property
    def repeats_indefinitely(self):
        return self.is_recurring and self.recurrence_count is None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['start_offset_days', 'id']
