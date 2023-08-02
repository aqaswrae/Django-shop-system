from django.urls import path , re_path
from verifictaions import views

urlpatterns = [
    # 生成图片验证码
    # http://127.0.0.1:8080/ver/image_code/14072742-4fb9-428d-8d3a-e304864b644d/
    re_path('^image_code/(?P<uuid>[\w-]+)/$' , views.ImageCodeView.as_view()),
    # 生成短信验证码
    # http://127.0.0.1:8080/ver/sms_code/17841687578/?uuid=a44c09a5-eccc-4a3b-90f0-ec92d53b99dd&image_code=kmwm
    re_path('^sms_code/(?P<mobile>1[3-9]\d{9})/$' , views.SMSCodeView.as_view()),
]