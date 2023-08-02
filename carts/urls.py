from django.urls import path
from carts import views

urlpatterns = [
    path('carts/' , views.CartsView.as_view() , name='info'),
    path('carts/selection/' , views.CartsSelectAllView.as_view())
]