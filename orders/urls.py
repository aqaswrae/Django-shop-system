from django.urls import path
from orders import views

urlpatterns = [
   path('orders/settlement' , views.OrdersSettlementView.as_view() , name='settlement'),
   path('orders/commit/',views.OrderCommitView.as_view()),
   path('orders/success/',views.OrderSuccessView.as_view()),

]