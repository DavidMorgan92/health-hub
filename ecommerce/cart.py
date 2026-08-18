from .models import Product


def get_cart(request):
    cart = request.session.get('cart', {})
    return cart if isinstance(cart, dict) else {}


def get_cart_count(request):
    return sum(int(quantity) for quantity in get_cart(request).values())


def get_cart_items(request):
    cart = get_cart(request)
    products = Product.objects.in_bulk(cart.keys())
    return [
        {'product': products[int(product_id)], 'quantity': int(quantity)}
        for product_id, quantity in cart.items()
        if int(product_id) in products
    ]
