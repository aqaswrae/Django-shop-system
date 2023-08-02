from django.urls import path
from areas import views

urlpatterns = [
    # 实现省市区的数据
    path('areas/' , views.AreasView.as_view()),
]