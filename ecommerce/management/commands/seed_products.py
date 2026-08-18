from decimal import Decimal

from django.core.management.base import BaseCommand

from ecommerce.models import Product


class Command(BaseCommand):
    help = 'Seed the database with sample health products.'

    def handle(self, *args, **options):
        products = [
            {
                'name': 'Vitamin C Gummies',
                'description': 'Daily immune support with citrus flavor and no artificial preservatives.',
                'price': Decimal('14.99'),
                'stock': 25,
            },
            {
                'name': 'Omega-3 Fish Oil',
                'description': 'High-potency omega-3 capsules for heart and brain wellness.',
                'price': Decimal('19.50'),
                'stock': 18,
            },
            {
                'name': 'Protein Blend Powder',
                'description': 'Vanilla plant-based protein powder with added digestive enzymes.',
                'price': Decimal('29.00'),
                'stock': 12,
            },
            {
                'name': 'Daily Greens',
                'description': 'A nutrient-rich blend of spinach, kale, spirulina, and superfoods.',
                'price': Decimal('24.75'),
                'stock': 20,
            },
            {
                'name': 'Electrolyte Hydration Tabs',
                'description': 'Hydration support with minerals for workouts and recovery.',
                'price': Decimal('12.25'),
                'stock': 30,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in products:
            obj, created = Product.objects.update_or_create(
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'stock': item['stock'],
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed complete: {created_count} created, {updated_count} updated.'
            )
        )
