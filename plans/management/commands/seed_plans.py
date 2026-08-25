from django.core.management.base import BaseCommand

from ecommerce.models import Product
from plans.models import Plan, PlanEvent


NUTRITION_EXAMPLES = [
    [
        {
            'title': 'Breakfast',
            'instructions': 'Start the day with a protein-rich breakfast and a glass of water.',
            'start_offset_days': 0,
            'recurrence_interval_days': 1,
            'recurrence_count': None,
            'linked_products': ['Protein Blend Powder'],
        },
        {
            'title': 'Meal preparation',
            'instructions': 'Prepare balanced lunches and snacks for the next three days.',
            'start_offset_days': 0,
            'duration_days': 2,
            'recurrence_interval_days': 7,
            'recurrence_count': 4,
            'linked_products': [],
        },
        {
            'title': 'Weekly check-in',
            'instructions': 'Review energy, hunger, and adherence, then adjust portions if needed.',
            'start_offset_days': 6,
            'recurrence_interval_days': 7,
            'recurrence_count': 4,
            'linked_products': [],
        },
    ],
    [
        {
            'title': 'Hydration routine',
            'instructions': 'Drink water regularly throughout the day and include electrolytes after training.',
            'start_offset_days': 0,
            'recurrence_interval_days': 1,
            'recurrence_count': 28,
            'linked_products': ['Electrolyte Hydration Tabs'],
        },
        {
            'title': 'High-protein meal',
            'instructions': 'Build one meal around a lean protein, vegetables, and a satisfying whole-food carbohydrate.',
            'start_offset_days': 0,
            'recurrence_interval_days': 1,
            'recurrence_count': None,
            'linked_products': ['Protein Blend Powder'],
        },
        {
            'title': 'Progress review',
            'instructions': 'Record measurements and reflect on sleep, appetite, and consistency.',
            'start_offset_days': 13,
            'recurrence_interval_days': 14,
            'recurrence_count': 2,
            'linked_products': [],
        },
    ],
    [
        {
            'title': 'Plant-based breakfast',
            'instructions': 'Choose a breakfast with fruit, plant protein, and a source of healthy fat.',
            'start_offset_days': 0,
            'recurrence_interval_days': 1,
            'recurrence_count': None,
            'linked_products': ['Daily Greens'],
        },
        {
            'title': 'Fibre focus',
            'instructions': 'Include vegetables, beans, or whole grains in two meals today.',
            'start_offset_days': 0,
            'recurrence_interval_days': 1,
            'recurrence_count': None,
            'linked_products': ['Fiber + Greens'],
        },
        {
            'title': 'Meal plan refresh',
            'instructions': 'Choose recipes and prepare ingredients for the week ahead.',
            'start_offset_days': 6,
            'recurrence_interval_days': 7,
            'recurrence_count': 4,
            'linked_products': [],
        },
    ],
]

EXERCISE_EXAMPLES = [
    [
        {
            'title': 'Strength session',
            'instructions': 'Complete three rounds of squat, push, pull, hinge, and carry movements with controlled form.',
            'start_offset_days': 0,
            'recurrence_interval_days': 3,
            'recurrence_count': 8,
            'linked_products': ['Adjustable Dumbbell Pair'],
        },
        {
            'title': 'Mobility routine',
            'instructions': 'Spend ten minutes moving through hips, shoulders, and thoracic spine.',
            'start_offset_days': 1,
            'recurrence_interval_days': 2,
            'recurrence_count': None,
            'linked_products': ['Yoga Mat Pro'],
        },
        {
            'title': 'Recovery day',
            'instructions': 'Take an easy walk and complete gentle stretching without pushing into pain.',
            'start_offset_days': 2,
            'recurrence_interval_days': 3,
            'recurrence_count': 8,
            'linked_products': ['Foam Roller Deluxe'],
        },
    ],
    [
        {
            'title': 'HIIT workout',
            'instructions': 'Complete eight rounds of 30 seconds work and 30 seconds recovery, then cool down.',
            'start_offset_days': 0,
            'recurrence_interval_days': 2,
            'recurrence_count': 12,
            'linked_products': ['Jump Rope Pro'],
        },
        {
            'title': 'Low-intensity movement',
            'instructions': 'Take a twenty-minute walk and finish with relaxed mobility work.',
            'start_offset_days': 1,
            'recurrence_interval_days': 1,
            'recurrence_count': None,
            'linked_products': [],
        },
        {
            'title': 'Core finisher',
            'instructions': 'Complete three controlled rounds of plank, dead bug, side plank, and bird dog.',
            'start_offset_days': 3,
            'recurrence_interval_days': 4,
            'recurrence_count': 6,
            'linked_products': ['Yoga Mat Pro'],
        },
    ],
    [
        {
            'title': 'Progressive lifting',
            'instructions': 'Complete the prescribed sets and add a small amount of load only when every repetition is controlled.',
            'start_offset_days': 0,
            'recurrence_interval_days': 2,
            'recurrence_count': 18,
            'linked_products': ['Adjustable Dumbbell Pair', 'Workout Bench Foldable'],
        },
        {
            'title': 'Accessory work',
            'instructions': 'Train smaller muscle groups with moderate effort and leave two repetitions in reserve.',
            'start_offset_days': 1,
            'recurrence_interval_days': 3,
            'recurrence_count': 12,
            'linked_products': ['Resistance Bands Set'],
        },
        {
            'title': 'Deload and recover',
            'instructions': 'Reduce training volume, walk lightly, and prioritise sleep and hydration.',
            'start_offset_days': 5,
            'duration_days': 2,
            'recurrence_interval_days': 7,
            'recurrence_count': 4,
            'linked_products': ['Foam Roller Deluxe'],
        },
    ],
]


class Command(BaseCommand):
    help = 'Seed example schedules for every nutrition and exercise plan product.'

    def handle(self, *args, **options):
        products = Product.objects.filter(
            product_type__in=[
                Product.ProductType.NUTRITION_PLAN,
                Product.ProductType.EXERCISE_PLAN,
            ],
        ).order_by('id')
        linked_products = Product.objects.in_bulk(
            Product.objects.filter(
                product_type__in=[
                    Product.ProductType.NUTRITION_PRODUCT,
                    Product.ProductType.EXERCISE_PRODUCT,
                ],
            ).values_list('id', flat=True),
        )
        linked_products_by_name = {product.name: product for product in linked_products.values()}

        plans_created = 0
        events_created = 0
        for product in products:
            plan, created = Plan.objects.get_or_create(product=product)
            plans_created += int(created)
            plan.events.all().delete()

            examples = (
                NUTRITION_EXAMPLES if product.product_type == Product.ProductType.NUTRITION_PLAN
                else EXERCISE_EXAMPLES
            )
            example = examples[(product.id - 1) % len(examples)]
            for event_data in example:
                event_fields = {
                    key: value
                    for key, value in event_data.items()
                    if key != 'linked_products'
                }
                event = PlanEvent.objects.create(plan=plan, **event_fields)
                event.linked_products.set(
                    linked_products_by_name[name]
                    for name in event_data['linked_products']
                    if name in linked_products_by_name
                )
                events_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete: {plans_created} plans created, {events_created} events created.'
        ))
