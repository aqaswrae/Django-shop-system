from django import forms

# 认证用户注册信息
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20 , min_length=5 , required=True,
                               error_messages={
                                   "max_length" : "用户名过长，最长为20",
                                   "min_length" : "用户名过短，最短为5"
                               })
    password = forms.CharField(max_length=20, min_length=8, required=True,
                               error_messages={
                                   "max_length": "密码过长，最长为20",
                                   "min_length": "密码过短，最短为8"
                               })
    password2 = forms.CharField(max_length=20, min_length=8, required=True,
                               error_messages={
                                   "max_length": "密码过长，最长为20",
                                   "min_length": "密码过短，最短为8"
                               })
    mobile = forms.CharField(min_length=11 , max_length=11 , required=True,
                            error_messages = {
                                "max_length": "手机号码不正确",
                                "min_length": "手机号码不正确"
                            })
    sms_code = forms.CharField(min_length=6 , max_length=6 , required=True)

    # 使用全局钩子
    # 验证两次密码是否一致
    def clean(self):
        cleand_data = super().clean()
        password = cleand_data.get('password')
        password2 = cleand_data.get('password2')
        if password != password2:
            raise forms.ValidationError('密码输入不一致')
        return cleand_data


# 认证用户登录信息
class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=5)
    password = forms.CharField(max_length=20, min_length=8)
    remembered = forms.BooleanField(required=False)