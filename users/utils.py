from django.contrib.auth.backends import ModelBackend
from users.models import User
import re
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def get_user_by_account(account):
    # 判断数据是用户名还是手机号
    try:
        if re.match('^1[3-9]\d{9}$' , account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except Exception:
        return None
    return user

class UsernameMobileBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 调用方法 ， 获得用户数据
        user = get_user_by_account(username)

        if user and user.check_password(password):
            return user
        else:
            return None

def generate_verify_email_url(user):
    # 生成邮箱激活链接
    s = Serializer(settings.SECRET_KEY , 600)
    # 获得用户数据
    data = {'user_id':user.id , 'email':user.email}
    # 制作加密数据
    token = s.dumps(data)
    return settings.EMAIL_VERIFY_URL +'?token='+token.decode()

def check_verify_email_token(token):
    # 将token序列化的用户信息进行反序列化 吗获得用户的信息
    s = Serializer(settings.SECRET_KEY , 600)
    try:
        data = s.loads(token)
    except Exception:
        return None

    else:
        user_id = data.get('user_id')
        email = data.get('email')
        # 从数据库中获取这个用户对象
        try:
            user = User.objects.get(id=user_id , email=email)
        except Exception:
            return None
        else:
            return user



