from django.shortcuts import render
from django.db.models import Q
from .models import Product

def store(request):
    """Main store page grouped into one section for each product type."""
    sections = [
        {
            'title': 'Nutrition Plans',
            'type': Product.ProductType.NUTRITION_PLAN,
            'products': Product.objects.filter(
                product_type=Product.ProductType.NUTRITION_PLAN,
            )[:5],
        },
        {
            'title': 'Exercise Plans',
            'type': Product.ProductType.EXERCISE_PLAN,
            'products': Product.objects.filter(
                product_type=Product.ProductType.EXERCISE_PLAN,
            )[:5],
        },
        {
            'title': 'Nutrition Products',
            'type': Product.ProductType.NUTRITION_PRODUCT,
            'products': Product.objects.filter(
                product_type=Product.ProductType.NUTRITION_PRODUCT,
            )[:5],
        },
        {
            'title': 'Exercise Products',
            'type': Product.ProductType.EXERCISE_PRODUCT,
            'products': Product.objects.filter(
                product_type=Product.ProductType.EXERCISE_PRODUCT,
            )[:5],
        },
    ]
    context = {'sections': sections}
    return render(request, 'ecommerce/store.html', context)


def product_search(request):
    query = request.GET.get('q', '').strip()
    product_type = request.GET.get('product_type', '').strip()
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
        )
    if product_type in Product.ProductType.values:
        products = products.filter(product_type=product_type)
    elif product_type:
        products = products.none()

    context = {
        'products': products,
        'query': query,
        'product_type': product_type,
    }
    return render(request, 'ecommerce/search.html', context)

def cart_detail(request):
    """View for displaying the shopping cart details"""
    # Assuming you have a way to get the cart items, e.g., from session or database
    cart_items = request.session.get('cart', [])
    context = {'cart_items': cart_items}
    return render(request, 'ecommerce/cart_detail.html', context)
