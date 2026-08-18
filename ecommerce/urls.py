from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.product_search, name='product_search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]
