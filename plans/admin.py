from django.contrib import admin

from .models import Plan, PlanEvent


class PlanEventInline(admin.TabularInline):
    model = PlanEvent
    extra = 0
    autocomplete_fields = ('linked_products',)
    fields = (
        'title',
        'instructions',
        'start_offset_days',
        'duration_days',
        'recurrence_interval_days',
        'recurrence_count',
        'linked_products',
    )


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_type', 'event_count')
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)
    inlines = (PlanEventInline,)

    @admin.display(description='Type')
    def product_type(self, obj):
        return obj.product.get_product_type_display()

    @admin.display(description='Events')
    def event_count(self, obj):
        return obj.events.count()


@admin.register(PlanEvent)
class PlanEventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'plan',
        'start_offset_days',
        'duration_days',
        'recurrence_interval_days',
        'recurrence_count',
    )
    list_filter = ('plan__product__product_type',)
    search_fields = ('title', 'instructions', 'plan__product__name')
    autocomplete_fields = ('plan', 'linked_products')
