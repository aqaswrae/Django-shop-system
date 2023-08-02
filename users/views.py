from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from users import forms
from users.models import User, Address
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse, HttpResponseForbidden
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
import json, re
from utils.response_code import RETCODE
from django.core.mail import send_mail
from django.conf import settings
from utils.views import LoginRequiredJsonMixin
from users.utils import generate_verify_email_url, check_verify_email_token

class RegisterView(View):
    def get(self, request):
        # 用于响应用户注册页面
        return render(request, 'register.html')

    def post(self, request):
        # 用户注册信息的校验
        # 检验数据  使用自定义的forms表单类校验
        # forms表单类接收的数据类型为：字典类型
        register_form = forms.RegisterForm(request.POST)

        # 校验数据是否合法； 合法则将数据保存到数据库中，注册成功； 不合法则注册失败
        # is_valid()
        if register_form.is_valid():
            # 说明数据合法 ， 获取数据
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password')
            mobile = register_form.cleaned_data.get('mobile')

            # 获取用户输入的短信验证码的数据
            sms_code_client = register_form.cleaned_data.get('sms_code')
            # 获取保存在redis 数据库中的验证码
            redis_conn = get_redis_connection('ver_code')
            sms_code_server = redis_conn.get('image_%s' % mobile)
            # 判断短信验证码是否有效
            if sms_code_server is None:
                return render(request, 'register.html', {'sms_code_errmsg': '短信验证已失效'})
            # 进行校验短信验证码
            if sms_code_server.decode() != sms_code_client:
                return render(request, 'register.html', {'sms_code_errmsg': '短信验证码错误'})

            # 把数据保存到数据库中
            try:
                user = User.objects.create_user(username=username, password=password, mobile=mobile)
            except Exception as e:
                return render(request, 'register.html', {'register_error': '注册失败'})

            # 实现状态保持
            login(request, user)

            # 响应数据注册成功
            return redirect('index')

        else:
            # 获取表单错误信息
            context = {'forms_error': register_form.errors}
            return render(request, 'register.html', context=context)

class UsernameCountView(View):
    # 判断用户名是否重复
    def get(self, request, username):
        # 从请求中获取到用户名
        # 从数据库中查看这个用户名是否存在
        count = User.objects.filter(username=username).count()
        # 前端vue中发送的是ajax请求 ， 接收的是json数据
        return JsonResponse({'code': 200, 'errmsg': 'OK', 'count': count})

class LoginView(View):
    # 用户登录
    def get(self, request):
        # 实现登录页面
        return render(request, 'login.html')

    def post(self, request):
        # 接收请求找那个的参数进行校验
        login_form = forms.LoginForm(request.POST)
        # 判断数据是否正确
        if login_form.is_valid():
            # 提取表单中的数据
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            remembered = login_form.cleaned_data.get('remembered')

            # 判断获取的数据是否全部完整
            if not all([username, password]):
                return HttpResponseForbidden('缺少必要的数据')

            # 认证用户的数据信息是否正确
            # authenticate  ， 用户存在返回用户信息 ， 用户不存在返回None
            user = authenticate(username=username, password=password)
            if user is None:
                return render(request, 'login.html', {'account_errmsg': '账号或者密码错误'})

            # 保持状态
            login(request, user)

            if remembered != True:
                # 不记住 ， 关闭即销毁
                request.session.set_expiry(0)
            else:
                # 记住 ， 状态保持默认为两周
                request.session.set_expiry(None)

            # 接收get请求中的next参数
            next = request.GET.get('next')
            # 通过get请求判断有没有next参数
            if next:
                response = redirect(next)
            else:
                # 重定向到首页
                response = redirect('index')

            # 讲用户数据写到cookie中
            response.set_cookie('username', user.username, 3600)
            return response
        else:
            # 获取表单错误信息
            context = {'forms_error': login_form.errors}
            return render(request, 'login.html', context=context)

class LogoutView(View):
    # 实现用户退出
    def get(self, request):
        # 清理状态保持的信息数据
        logout(request)
        # 退出登录重定向页面，登录或者首页
        response = redirect('index')
        # 删除cookie中的用户信息
        response.delete_cookie('username')
        # 响应数据
        return response

class UserInfoView(LoginRequiredMixin, View):
    # 实现用户中心
    def get(self, request):
        # 获取到用户信息
        context = {
            "username": request.user.username,
            "mobile": request.user.mobile,
            "email": request.user.email,
            "email_active": request.user.email_active,
        }
        return render(request, 'user_center_info.html', context=context)

class EmailView(LoginRequiredJsonMixin, View):
    # 添加邮箱
    def put(self, request):
        # put请求的参数数据在request的body中
        # 接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 校验参数
        if not re.match('^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseForbidden('邮箱错误')

        # 保存邮箱数据
        try:
            request.user.email = email
            request.user.save()
        except Exception:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '邮箱添加失败'})

        # 发送邮件 ， 进行邮箱验证
        subject = "邮箱验证激活"
        # 调用生成激活链接的方法
        verify_url = generate_verify_email_url(request.user)
        html_message = f"""
            <p>什么 ， 你说什么</p>
            <p>我说阿宸好帅</p>
            <p>你的邮箱{email} , 点击链接确定</p>
            <p><a href="{verify_url}">{verify_url}</p>
        """
        send_mail(subject, '', from_email=settings.EMAIL_FROM, recipient_list=[email, ],
                  html_message=html_message)

        # 响应页面数据
        return JsonResponse({'code': RETCODE.OK, 'errmsg': "OK"})

class VerifyEmailView(View):
    # 验证邮箱
    def get(self, request):
        # 接收路由中的token数据
        token = request.GET.get('token')
        # 判断路径是否带有token参数
        if not token:
            return HttpResponseForbidden('缺少token参数')
        # 调用解密的方法 ， 查询用户数据
        user = check_verify_email_token(token)
        # 判断用户是否已经进行邮箱验证
        if user.email_active == 0:
            # 邮箱没有激活 ， 设置值为True
            user.email_active = True
            user.save()
        else:
            # 邮箱已经激活
            return HttpResponseForbidden('邮箱已经被激活')
        # 响应结果
        return redirect('users:info')

class AddressView(View):
    # 用户收货地址
    def get(self, request):
        # 响应收货地址页面
        login_user = request.user
        count = Address.objects.filter(user=login_user , is_deleted=False).count()
        # 根据登录的用户 ， 获取对应的非删除的地址
        addresses = Address.objects.filter(user=login_user , is_deleted=False)
        address_list = []
        for address in addresses:
            address_dict = {
                'id': address.id,
                'receiver': address.title,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email
            }
            address_list.append(address_dict)
        context = {
            'addresses': address_list,
            'count':count,
            'default_address_id': login_user.default_address_id
        }
        return render(request, 'user_center_site.html',context)

class ChangePasswordView(View):
    # 修改密码
    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):
        # 实现修改密码的逻辑
        # 接收数据
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        # 检验数据
        # 判断数据是否全部获取
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden('缺少必要数据')
        # 判断就密码是否正确
        try:
            request.user.check_password(old_password)
        except Exception:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原来密码错误'})
        # 校验密码是否满足要求
        if not re.match('^[a-zA-Z0-9]{8,20}$', new_password):
            return HttpResponseForbidden('请输入8-20位的密码')
        # 校验两次密码是否一致
        if new_password != new_password2:
            return HttpResponseForbidden('两次密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '密码修改失败'})

        # 清理状态保持
        logout(request)
        response = redirect('users:login')
        response.delete_cookie('username')

        # 响应面修改结果，页面重定向到登录页面中
        return response

class AddressCreateView(LoginRequiredJsonMixin, View):
    # 用户新增地址
    def post(self, request):
        #判断用户地址是否超过上限
        count = Address.objects.filter(user=request.user).count()
        if count>20:
            return  JsonResponse({'code':RETCODE.THROTTLINGERR , 'errmsg':'地址数量过多'})
        # 接收请求中的参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数数据
        if not all([receiver, province_id, district_id, city_id, place, mobile]):
            return HttpResponseForbidden('缺少必要数据')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('固定电话有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('邮箱有误')

        # 将接收的参数保存到数据库中
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email)
            # 设置默认的收货地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception:
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 数据保存成功 ， 取出数据进行响应
        address_dict = {
            'id' :address.id,
            'receiver' : address.title,
            'province' : address.province.name,
            'city' : address.city.name,
            'district' : address.district.name,
            'place' : address.place,
            'mobile' : address.mobile,
            'tel' : address.tel,
            'email' : address.email
        }

        return  JsonResponse({'code':RETCODE.OK , 'errmsg':'新增地址成功' , 'address':address_dict})

class UpdateAddressView(LoginRequiredJsonMixin , View):
    # 修改地址
    def put(self , request , address_id):
        # 接收请求中的参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数数据
        if not all([receiver, province_id, district_id, city_id, place, mobile]):
            return HttpResponseForbidden('缺少必要数据')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseForbidden('固定电话有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseForbidden('邮箱有误')

        try:
            # 修改数据库中对应的数据
            address = Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception:
            return JsonResponse({'code':RETCODE.DBERR , 'errmsg':'修改地址失败'})

        address = Address.objects.get(id=address_id)
        # 数据保存成功 ， 取出数据进行响应
        address_dict = {
            'id': address.id,
            'receiver': address.title,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def delete(self , request , address_id):
        # 删除地址
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception:
            return JsonResponse({'code':RETCODE.DBERR , 'errmsg':'删除地址失败' })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})

class DefaultAddressView(LoginRequiredJsonMixin , View):
    # 设置用户默认地址
    def put(self , request , address_id):
        # 从数据库读取数据 ， 然后进行设置
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception:
            return JsonResponse({'code':RETCODE.DBERR , 'errmsg':'设置默认地址失败' })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})
