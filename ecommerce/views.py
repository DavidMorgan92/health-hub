from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .cart import get_cart, get_cart_count, get_cart_items
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
    cart_items = get_cart_items(request)
    context = {'cart_items': cart_items}
    return render(request, 'ecommerce/cart_detail.html', context)


def add_to_cart(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    current_quantity = int(cart.get(str(product_id), 0))

    if not product.is_plan and current_quantity >= product.stock:
        return JsonResponse({'error': 'This product is out of stock.', 'count': get_cart_count(request)}, status=400)

    cart[str(product_id)] = 1 if product.is_plan else current_quantity + 1
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'count': get_cart_count(request)})


def update_cart_quantity(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    if not product.allows_multiple_purchases:
        return JsonResponse({'error': 'This item cannot have its quantity adjusted.'}, status=400)

    try:
        quantity = int(request.POST.get('quantity', ''))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Quantity must be a whole number.'}, status=400)

    if quantity < 1:
        return JsonResponse({'error': 'Quantity must be at least one.'}, status=400)
    if quantity > product.stock:
        return JsonResponse({'error': 'There is not enough stock for that quantity.'}, status=400)

    cart = get_cart(request)
    if str(product_id) not in cart:
        return JsonResponse({'error': 'This item is not in your cart.'}, status=404)

    cart[str(product_id)] = quantity
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({
        'quantity': quantity,
        'total': f'£{product.price * quantity:.2f}',
        'count': get_cart_count(request),
    })


def remove_from_cart(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)

    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'count': get_cart_count(request)})


def empty_cart(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required.'}, status=405)

    request.session['cart'] = {}
    request.session.modified = True
    return JsonResponse({'count': 0})
