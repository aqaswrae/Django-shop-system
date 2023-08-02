from django.shortcuts import render , HttpResponse
from django.views import View
from verifictaions.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import JsonResponse
from utils.response_code import RETCODE
from verifictaions.ronglianyun.ccp_sms import sand_code
import random

class ImageCodeView(View):
    # 实现图片验证码
    def get(self , request , uuid):
        text , image = captcha.generate_captcha()
        # 保存验证码，保存到redis ， 要到配置文件中 ，
        # 配置一个专门保存验证的数据库
        # redis中有16个数据库 ， 名称：0 - 15
        # 获取redis数据库链接
        redis_conn = get_redis_connection('ver_code')
        # setex(key , time , value)
        redis_conn.setex('image_%s'%uuid , 400 , text)
        # 响应到对应的浏览器中
        return HttpResponse(image , content_type='image/png')


class SMSCodeView(View):
    # 短信验证码
    def get(self , request , mobile):
        # 接收uuid ，图片验证码 , 这个两个参数必须传递过来
        uuid = request.GET.get('uuid')
        image_code_client = request.GET.get('image_code')
        # 检验指定的列表中的数据是否都有
        if not all([uuid , image_code_client]):
            return HttpResponse('缺少必要数据')

        # 在生成短信验证码之前拍段图片验证码是否正确
        # 从redis中获取图片验证码
        redis_conn = get_redis_connection('ver_code')
        image_code_server = redis_conn.get('image_%s'%uuid)

        # 提取判断用户是否频繁请求短信验证码
        send_flag = redis_conn.get('senf_flag_%s'% mobile)
        if send_flag:
            return JsonResponse({'code':RETCODE.THROTTLINGERR,
                                 'errsg':'发送短信验证码过于频繁'})

        # 判断图片验证码是否失效
        if image_code_server is None:
            return JsonResponse({'code':RETCODE.IMAGECODEERR,
                                 'errsg':'图片验证码已失效'})

        # 删除图片验证码
        redis_conn.delete('image_%s'%uuid)

        # 校验图片验证码
        # 将redis提取的数据进行转码
        image_code_server = image_code_server.decode()
        if image_code_server.lower() != image_code_client.lower():
            return JsonResponse({'code':RETCODE.IMAGECODEERR,
                                 'errsg':'图片验证码输入有误'})

        # 生成短信验证码
        sms_code = '%06d'%random.randint(0 , 999999)

        # 保存短信验证码
        redis_conn.setex('image_%s'%mobile , 400 , sms_code)
        # 保存一个键值对 ， 表示已经发送了验证码
        redis_conn.setex('senf_flag_%s'% mobile , 60 , 1)

        # 发送短信
        sand_code.send_message(mobile , (sms_code , 5) , 1)

        # 响应
        return JsonResponse({'code':RETCODE.OK,
                                 'errsg':'短信验证码发送成功'})

