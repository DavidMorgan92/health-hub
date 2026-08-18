from django.db import models
from django.core.exceptions import ValidationError


class Product(models.Model):
    class ProductType(models.TextChoices):
        NUTRITION_PLAN = 'nutrition_plan', 'Nutrition plan'
        EXERCISE_PLAN = 'exercise_plan', 'Exercise plan'
        NUTRITION_PRODUCT = 'nutrition_product', 'Nutrition product'
        EXERCISE_PRODUCT = 'exercise_product', 'Exercise product'

    name = models.CharField(max_length=200)
    description = models.TextField()
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.EXERCISE_PRODUCT,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='One-off price for nutrition and exercise products.',
    )
    subscription_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Monthly subscription price for nutrition and exercise plans.',
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.is_plan:
            if self.subscription_price is None:
                raise ValidationError({'subscription_price': 'Plans must have a monthly subscription price.'})
            if self.price is not None:
                raise ValidationError({'price': 'Plans cannot have a one-off price.'})
        else:
            if self.price is None:
                raise ValidationError({'price': 'Products must have a one-off price.'})
            if self.subscription_price is not None:
                raise ValidationError({'subscription_price': 'Products cannot have a subscription price.'})

    @property
    def is_plan(self):
        return self.product_type in {
            self.ProductType.NUTRITION_PLAN,
            self.ProductType.EXERCISE_PLAN,
        }

    @property
    def allows_multiple_purchases(self):
        return not self.is_plan

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(
                        product_type__in=[
                            'nutrition_plan',
                            'exercise_plan',
                        ],
                        price__isnull=True,
                        subscription_price__isnull=False,
                    )
                    | models.Q(
                        product_type__in=[
                            'nutrition_product',
                            'exercise_product',
                        ],
                        price__isnull=False,
                        subscription_price__isnull=True,
                    )
                ),
                name='product_type_has_matching_price',
            ),
        ]
