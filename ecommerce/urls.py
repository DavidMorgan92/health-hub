from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.product_search, name='product_search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/empty/', views.empty_cart, name='empty_cart'),
]
