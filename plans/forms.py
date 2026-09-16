from django import forms

from ecommerce.models import Product
from .models import PlanEvent


class PlanProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'product_type', 'subscription_price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'subscription_price': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'},
            ),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_type'].choices = [
            (Product.ProductType.NUTRITION_PLAN, Product.ProductType.NUTRITION_PLAN.label),
            (Product.ProductType.EXERCISE_PLAN, Product.ProductType.EXERCISE_PLAN.label),
        ]
        self.fields['subscription_price'].label = 'Monthly subscription price'
        self.fields['image'].required = False

    def clean_name(self):
        name = self.cleaned_data['name']
        if Product.objects.filter(name=name).exists():
            raise forms.ValidationError('A product with this name already exists.')
        return name


class PlanEventForm(forms.ModelForm):
    class Meta:
        model = PlanEvent
        fields = [
            'title',
            'instructions',
            'start_offset_days',
            'duration_days',
            'recurrence_interval_days',
            'recurrence_count',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'start_offset_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'recurrence_interval_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'recurrence_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_offset_days'].initial = 0
        self.fields['duration_days'].initial = 1
        self.fields['recurrence_interval_days'].required = False
        self.fields['recurrence_count'].required = False
