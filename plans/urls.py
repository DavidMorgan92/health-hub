from django.urls import path

from . import views

app_name = 'plans'

urlpatterns = [
    path('', views.home, name='plans_home'),
]
