from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from utils.response_code import RETCODE

class LoginRequiredJsonMixin(LoginRequiredMixin):
    # 自定义登的判断用户是否录的类：返回的是Json数据
    def handle_no_permission(self):
        return JsonResponse({'code':RETCODE.SESSIONERR  , 'errmsg':'用户未登录'} )
