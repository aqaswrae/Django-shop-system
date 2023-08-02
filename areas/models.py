from django.db import models

class Ares(models.Model):
    # 省份市区模型
    name = models.CharField(max_length=20 , verbose_name='名称')
    # self ； 自关联
    # models.SET_NULL : 删除字段时，关联到的字段，设置为NULL
    parent = models.ForeignKey('self' , on_delete=models.SET_NULL,
                               related_name='subs' , null=True , blank=True ,
                               verbose_name='上级行政区划分')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name