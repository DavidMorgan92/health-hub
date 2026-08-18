from .cart import get_cart_count


def cart(request):
    return {'num_cart_items': get_cart_count(request)}
