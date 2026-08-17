from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

def store(request):
    """Main store page with all products"""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'ecommerce/store.html', context)
