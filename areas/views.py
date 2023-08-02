from django.shortcuts import render
from django.views import View
from areas.models import Ares
from django.http import JsonResponse
from utils.response_code import RETCODE
from django.core.cache import cache

class AreasView(View):
    # 实现省市区的数据
    def get(self , request):
        # 判断当前需要查询的数据是省份还是市区的
        area_id = request.GET.get('area_id')
        # 让程序从内存缓存中读取数据 ， 当内存没有这份数据的时候再从数据库中读取 ，
        # 并且从数据库读取数据之后缓存到内存中 ， 再进行响应
        if not area_id:
            # 先缓存中读取数据 ， 判断是否有数据存在
            province_list = cache.get('province_list')
            #  判断是否读取出来数据
            if not province_list:
                try:
                    # 查询省份数据
                    province_model_list = Ares.objects.filter(parent_id__isnull=True)
                    '''
                    返回的json数据格式
                    {
                    'code':'0'
                    'errmsg':'OK'
                    'province_list':[
                        {
                            'id' : 110000,
                            'name': '北京市'
                        }，
                        ……
                    ]
                    }
                    '''
                    # 从获得到的数据对象中取出id ， name ， 构造一个json数据
                    province_list = []
                    # 直接讲对象进行返回 ， 在json中是不允许的。需要提取出需要的数据保存到序列中
                    for province_model in province_model_list:
                        province_dict = {
                            "id": province_model.id,
                            "name": province_model.name
                        }
                        province_list.append(province_dict)
                    # 将从数据库中读取的数据缓存到内存中
                    cache.set('province_list' , province_list , 3600)
                    # 响应数据
                    # return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
                except Exception:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                try:
                    # 查询市区的数据
                    parent_model = Ares.objects.get(id=area_id)
                    # 根据获得的对象查询关联到他的数据
                    sub_model_list = parent_model.subs.all()
                    '''
                    返回的json数据格式
                    {
                        'code':'0'
                        'errmsg':'OK'
                        'sub_data':{
                            省
                            'id' : 110000,
                            'name': '北京市'
                            'subs':[
                                {   市区
                                    'id' : 110000,
                                    'name': '北京市'
                                }，
                            ……
                            ]
                        }
                    }
                    '''
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            'id': sub_model.id,
                            'name': sub_model.name
                        }
                        subs.append(sub_dict)

                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs
                    }
                    cache.set('sub_area_' + area_id , sub_data , 3600)
                    # return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
                except Exception:
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询市区数据错误'})
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})




