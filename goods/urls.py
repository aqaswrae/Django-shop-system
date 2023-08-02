from django.urls import path , re_path
from goods import views

urlpatterns = [
    # 商品列表页
    re_path('^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$' , views.GoodsListView.as_view() , name='list'),
    #  商品热销排行
    re_path('^hot/(?P<category_id>\d+)/$' , views.HotGoodsView.as_view()),
    # 商品详情页
    re_path('^detail/(?P<sku_id>\d+)/$' , views.DetaiGoodsView.as_view() , name='detail'),
    # 商品访问量
    re_path('^detail/visit/(?P<category_id>\d+)/$',views.DetailVisitView.as_view()),
]