from django.contrib import admin

from .models import Subscription, SubscriptionPlan


class SubscriptionPlanInline(admin.TabularInline):
    model = SubscriptionPlan
    extra = 0
    autocomplete_fields = ('plan',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'status',
        'stripe_status',
        'current_period_end',
        'cancel_at_period_end',
        'stripe_subscription_id',
    )
    list_filter = ('status', 'cancel_at_period_end')
    search_fields = (
        'user__username',
        'user__email',
        'stripe_subscription_id',
        'stripe_customer_id',
    )
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = (SubscriptionPlanInline,)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('plan', 'subscription', 'stripe_subscription_item_id')
    search_fields = (
        'plan__product__name',
        'subscription__user__username',
        'stripe_subscription_item_id',
    )
    autocomplete_fields = ('subscription', 'plan')
