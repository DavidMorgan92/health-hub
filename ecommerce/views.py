from django.shortcuts import render
from django.views.generic import ListView
from .models import Product

def store(request):
    """Main store page with all products"""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'ecommerce/store.html', context)

def cart_detail(request):
    """View for displaying the shopping cart details"""
    # Assuming you have a way to get the cart items, e.g., from session or database
    cart_items = request.session.get('cart', [])
    context = {'cart_items': cart_items}
    return render(request, 'ecommerce/cart_detail.html', context)
