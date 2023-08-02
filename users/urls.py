from django.urls import path , re_path
from users import views

app_name = 'users'

urlpatterns = [
    # 用户注册
    path('register/' ,views.RegisterView.as_view() , name='register'),
    # 判断用户名是否重复的
    # http://127.0.0.1:8080/users/username/rootac/count/
    re_path('^username/(?P<username>[a-zA-Z0-9-_]{5,20})/count/$' , views.UsernameCountView.as_view()),
    # 用户登录
    path('login/' , views.LoginView.as_view() , name='login'),
    # 用户退出登录
    path('logout/' , views.LogoutView.as_view() , name='logout'),
    # 用户中心
    path('info/' , views.UserInfoView.as_view() , name='info'),
    # 添加邮箱
    path('email/' , views.EmailView.as_view()),
    # 验证邮箱
    path('emails/verification/' , views.VerifyEmailView.as_view()),
    # 用户收货地址
    path('address/' , views.AddressView.as_view() , name='address'),
    # 修改密码
    path('changepwd/' , views.ChangePasswordView.as_view() , name='changepwd'),
    # 用户新增地址
    path('addresses/create/',views.AddressCreateView.as_view()),
    # 用户修改地址
    re_path('^addresses/(?P<address_id>\d+)/$',views.UpdateAddressView.as_view()),
    # 设置用户默认地址
    re_path('^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
]