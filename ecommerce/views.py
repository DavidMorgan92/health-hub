import stripe
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.urls import reverse
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
    cart_total = sum(
        (
            item['product'].subscription_price
            if item['product'].is_plan
            else item['product'].price
        ) * item['quantity']
        for item in cart_items
    ) if cart_items else Decimal('0')
    context = {'cart_items': cart_items, 'cart_total': cart_total}
    return render(request, 'ecommerce/cart_detail.html', context)


def checkout(request):
    cart_items = get_cart_items(request)
    if not cart_items:
        messages.info(request, 'Add an item to your cart before checking out.')
        return redirect('ecommerce:cart_detail')

    if request.method == 'POST':
        for item in cart_items:
            if not item['product'].is_plan and item['quantity'] > item['product'].stock:
                messages.error(
                    request,
                    f'There is not enough stock for {item["product"].name}.',
                )
                return redirect('ecommerce:cart_detail')

        if not settings.STRIPE_SECRET_KEY:
            messages.error(request, 'Stripe payments are not configured yet.')
            return render(request, 'ecommerce/checkout.html', {'cart_items': cart_items})

        line_items = []
        has_plan = False
        for item in cart_items:
            product = item['product']
            price = product.subscription_price if product.is_plan else product.price
            price_data = {
                'currency': settings.STRIPE_CURRENCY,
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(price * 100),
            }
            if product.is_plan:
                has_plan = True
                price_data['recurring'] = {'interval': 'month'}

            line_items.append({
                'price_data': price_data,
                'quantity': item['quantity'],
            })

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_data = {
            'mode': 'subscription' if has_plan else 'payment',
            'line_items': line_items,
            'success_url': request.build_absolute_uri(
                reverse('ecommerce:checkout_success'),
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': request.build_absolute_uri(reverse('ecommerce:checkout_cancel')),
        }
        if request.user.is_authenticated and request.user.email:
            session_data['customer_email'] = request.user.email

        session = stripe.checkout.Session.create(**session_data)
        request.session['stripe_checkout_session_id'] = session.id
        request.session.modified = True
        return redirect(session.url)

    return render(request, 'ecommerce/checkout.html', {'cart_items': cart_items})


def checkout_success(request):
    session_id = request.GET.get('session_id')
    if (
        not session_id
        or session_id != request.session.get('stripe_checkout_session_id')
        or not settings.STRIPE_SECRET_KEY
    ):
        return render(request, 'ecommerce/checkout_result.html', {'success': False})

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status != 'paid':
        return render(request, 'ecommerce/checkout_result.html', {'success': False})

    request.session['cart'] = {}
    request.session.pop('stripe_checkout_session_id', None)
    request.session.modified = True
    return render(request, 'ecommerce/checkout_result.html', {'success': True})


def checkout_cancel(request):
    return render(request, 'ecommerce/checkout_result.html', {'success': False})


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
