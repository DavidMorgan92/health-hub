from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart_detail, name='cart_detail'),
]
