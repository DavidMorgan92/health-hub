from django.urls import path

from . import views

app_name = 'plans'

urlpatterns = [
    path('', views.home, name='plans_home'),
    path('create/', views.create_plan, name='create_plan'),
    path('<int:pk>/', views.detail, name='plan_detail'),
]
