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
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('14.99'),
                'stock': 25,
            },
            {
                'name': 'Omega-3 Fish Oil',
                'description': 'High-potency omega-3 capsules for heart and brain wellness.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('19.50'),
                'stock': 18,
            },
            {
                'name': 'Protein Blend Powder',
                'description': 'Vanilla plant-based protein powder with added digestive enzymes.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('29.00'),
                'stock': 12,
            },
            {
                'name': 'Daily Greens',
                'description': 'A nutrient-rich blend of spinach, kale, spirulina, and superfoods.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('24.75'),
                'stock': 20,
            },
            {
                'name': 'Electrolyte Hydration Tabs',
                'description': 'Hydration support with minerals for workouts and recovery.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('12.25'),
                'stock': 30,
            },
            {
                'name': 'Collagen Peptides',
                'description': 'Unflavored collagen support for skin, joints, and recovery.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('27.50'),
                'stock': 16,
            },
            {
                'name': 'Magnesium Complex',
                'description': 'Balanced magnesium formula for calm recovery and muscle support.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('18.00'),
                'stock': 22,
            },
            {
                'name': 'Probiotic Gut Balance',
                'description': 'Daily probiotic blend to support digestion and immune health.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('21.95'),
                'stock': 14,
            },
            {
                'name': 'BCAA Recovery Fuel',
                'description': 'Refreshing branched-chain amino acid formula for active recovery.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('31.25'),
                'stock': 10,
            },
            {
                'name': 'Fiber + Greens',
                'description': 'A prebiotic fiber blend with greens for daily gut and energy support.',
                'product_type': Product.ProductType.NUTRITION_PRODUCT,
                'price': Decimal('23.40'),
                'stock': 19,
            },
            {
                'name': 'Lean Nutrition Reset',
                'description': 'A 4-week meal plan focused on balanced calories and sustainable habits.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('39.00'),
                'stock': 0,
            },
            {
                'name': 'High Protein Meal Prep',
                'description': 'Structured weekly nutrition plan for muscle gain and consistent energy.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('49.00'),
                'stock': 0,
            },
            {
                'name': 'Plant-Powered Balance',
                'description': 'Vegan nutrition guidance for weight management and digestive wellness.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('42.50'),
                'stock': 0,
            },
            {
                'name': 'Gluten-Free Wellness Plan',
                'description': 'A gluten-free nutrition roadmap for energy, digestion, and weight support.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('44.00'),
                'stock': 0,
            },
            {
                'name': 'Low-Carb Fat Loss Plan',
                'description': 'A calorie-conscious meal framework for steady fat loss and satiety.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('46.75'),
                'stock': 0,
            },
            {
                'name': 'Family Nutrition Essentials',
                'description': 'Balanced weekly meal planning for whole-family healthy eating.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('52.00'),
                'stock': 0,
            },
            {
                'name': 'Performance Fuel Plan',
                'description': 'Nutrition strategy designed for endurance athletes and active lifestyles.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('58.00'),
                'stock': 0,
            },
            {
                'name': 'Heart Healthy Nutrition',
                'description': 'A Mediterranean-inspired nutrition plan for cardiovascular support.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('54.25'),
                'stock': 0,
            },
            {
                'name': 'Immune Boost Nutrition',
                'description': 'Seasonal nutrition plan with foods and routines for immune resilience.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('45.50'),
                'stock': 0,
            },
            {
                'name': 'Postpartum Recovery Nutrition',
                'description': 'Recover-focused nutrition guidance for maternal energy and vitality.',
                'product_type': Product.ProductType.NUTRITION_PLAN,
                'subscription_price': Decimal('59.00'),
                'stock': 0,
            },
            {
                'name': 'Strength Foundation Plan',
                'description': 'Progressive training roadmap for beginners focused on strength and form.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('38.00'),
                'stock': 0,
            },
            {
                'name': 'Home HIIT Challenge',
                'description': 'Short, effective interval workouts designed for home training sessions.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('29.00'),
                'stock': 0,
            },
            {
                'name': 'Muscle Gain Blueprint',
                'description': 'Progressive hypertrophy plan with exercise selection and recovery guidance.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('57.00'),
                'stock': 0,
            },
            {
                'name': 'Core & Mobility Reset',
                'description': 'Targeted mobility and core routine for posture and movement quality.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('34.50'),
                'stock': 0,
            },
            {
                'name': '12-Week Body Transformation',
                'description': 'Full-body fitness system for fat loss, muscle retention, and confidence.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('64.00'),
                'stock': 0,
            },
            {
                'name': 'Athletic Conditioning Program',
                'description': 'High-output conditioning plan for speed, agility, and work capacity.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('63.50'),
                'stock': 0,
            },
            {
                'name': 'Desk Worker Recovery Plan',
                'description': 'Movement and exercise routine to relieve tension and improve posture.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('27.00'),
                'stock': 0,
            },
            {
                'name': 'Runner Performance Builder',
                'description': 'Run-specific conditioning and strength plan for endurance improvements.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('55.00'),
                'stock': 0,
            },
            {
                'name': 'Posture Perfect Program',
                'description': 'Alignment-focused training plan to reduce strain and improve movement.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('41.50'),
                'stock': 0,
            },
            {
                'name': 'Functional Fitness Evolution',
                'description': 'Everyday movement plan to build stamina, balance, and coordination.',
                'product_type': Product.ProductType.EXERCISE_PLAN,
                'subscription_price': Decimal('49.99'),
                'stock': 0,
            },
            {
                'name': 'Resistance Bands Set',
                'description': 'Portable set of loop bands for strength work, mobility, and rehab.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('24.99'),
                'stock': 35,
            },
            {
                'name': 'Yoga Mat Pro',
                'description': 'Non-slip exercise mat with extra cushioning for floor workouts.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('39.00'),
                'stock': 28,
            },
            {
                'name': 'Adjustable Dumbbell Pair',
                'description': 'Space-saving dumbbells for strength sessions and home workouts.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('89.00'),
                'stock': 12,
            },
            {
                'name': 'Kettlebell Power Kit',
                'description': 'Weighted kettlebell set for strength, conditioning, and mobility work.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('74.50'),
                'stock': 14,
            },
            {
                'name': 'Foam Roller Deluxe',
                'description': 'High-density foam roller for recovery, flexibility, and myofascial release.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('22.25'),
                'stock': 30,
            },
            {
                'name': 'Pull-Up Bar Doorway',
                'description': 'Compact doorway pull-up bar for upper-body strength at home.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('44.99'),
                'stock': 18,
            },
            {
                'name': 'Jump Rope Pro',
                'description': 'Smooth cardio rope with adjustable length for fast conditioning work.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('16.00'),
                'stock': 42,
            },
            {
                'name': 'Balance Board',
                'description': 'Stability board for balance training, core work, and coordination.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('32.75'),
                'stock': 21,
            },
            {
                'name': 'Medicine Ball Set',
                'description': 'Weighted medicine balls for explosive strength and conditioning drills.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('59.95'),
                'stock': 17,
            },
            {
                'name': 'Workout Bench Foldable',
                'description': 'Compact adjustable bench for strength and bodyweight training at home.',
                'product_type': Product.ProductType.EXERCISE_PRODUCT,
                'price': Decimal('119.00'),
                'stock': 8,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in products:
            defaults = {
                'description': item['description'],
                'product_type': item['product_type'],
                'stock': item.get('stock', 0),
                'price': item.get('price'),
                'subscription_price': item.get('subscription_price'),
            }

            obj, created = Product.objects.update_or_create(
                name=item['name'],
                defaults=defaults,
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
