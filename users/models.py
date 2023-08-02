from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.model import BaseModel

class User(AbstractUser):
    # 定义用户认证模型类
    mobile = models.CharField(max_length=11 , verbose_name='手机号')
    # 邮箱是否认证的字段
    email_active = models.BooleanField(default=False , verbose_name='邮箱验证状态')
    # 默认地址
    default_address = models.ForeignKey('Address' , related_name='users' , null=True , blank=True,
                                        on_delete=models.SET_NULL , verbose_name='默认地址')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class Address(BaseModel):
    # 用户地址
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='addresses' , verbose_name='用户')
    receiver = models.CharField(max_length=20 , verbose_name='收货人')
    title = models.CharField(max_length=20 , verbose_name='地址名称')
    province = models.ForeignKey('areas.Ares' , on_delete=models.PROTECT , related_name='province_addresses' , verbose_name='省')
    city = models.ForeignKey('areas.Ares' , on_delete=models.PROTECT , related_name='city_addresses' , verbose_name='市')
    district = models.ForeignKey('areas.Ares' , on_delete=models.PROTECT , related_name='district_addresses' , verbose_name='区')
    place = models.CharField(max_length=50 , verbose_name='地址')
    mobile = models.CharField(max_length=11 , verbose_name='手机')
    tel = models.CharField(max_length=20 , null=True , blank=True , default='' , verbose_name='固定电话')
    email = models.CharField(max_length=30 ,null=True , blank=True , default='' , verbose_name='邮箱' )
    is_deleted = models.BooleanField(default=False , verbose_name='删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']