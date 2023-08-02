from django.shortcuts import render
from django.views import View
from utils.views import LoginRequiredJsonMixin , LoginRequiredMixin
import json
from goods.models import SKU
from django.http import  HttpResponseForbidden , JsonResponse
from django_redis import get_redis_connection
from utils.response_code import RETCODE
from shop_system import settings

class CartsView(LoginRequiredJsonMixin , View):
    def get(self , request):
        #展示购物车页面
        # 获取用户对象
        user = request.user
        # 进入redis数据库中取出缓存的商品编号
        redis_conn = get_redis_connection('carts')
        # {id1:3 , id2:1}
        redis_cart = redis_conn.hgetall('cart_%s'% user.id)
        # {id2}
        redis_selected = redis_conn.smembers('selected_%s'% user.id)
        '''
        {
            "sku_id1":{
                "count" : "3"
                "selected":"False"
            },
            ……
        }
        '''
        cart_dict = {}
        for sku_id , count in redis_cart.items():
            cart_dict[int(sku_id)] = {
                "count": int(count),
                "selected": sku_id in redis_selected
            }
        # 获取所有商品id
        sku_ids = cart_dict.keys()
        # 获取所有商品对应数据对象
        skus = SKU.objects.filter(id__in = sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                # True , False
                # 为了方便前端json解析 ， 直接转换为 "True"
                "selected": str(cart_dict.get(sku.id).get('selected')),
                'name':sku.name,
                'price':str(sku.price),
                'default_image_url': settings.STATIC_URL + 'images/goods' + sku.default_image.url + '.jpg',
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus
        }
        return render(request , 'cart.html' , context=context)

    def post(self , request):
        # 添加购物车
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected' , True)

        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except Exception:
            return HttpResponseForbidden('参数sku_id错误')

        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('参数count错误')

        if selected:
            if not isinstance(selected , bool):
                return HttpResponseForbidden('参数selected错误')

        # 获取用户对象 ，做唯一标识
        user = request.user
        # 保存购物车
        redis_conn = get_redis_connection('carts')
        redis_conn.hincrby('cart_%s'% user.id , sku_id , count)

        if selected:
            redis_conn.sadd('selected_%s'% user.id , sku_id)

        return JsonResponse({'code':RETCODE.OK , 'errmsg':'OK'})

    def put(self , request):
        # 修改购物车
        # 接收参数
        # { sku_id: 3, count: 2, selected: false}
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('参数count错误')

        if selected:
            if not isinstance(selected , bool):
                return HttpResponseForbidden('参数selected错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception:
            return HttpResponseForbidden('参数sku_id错误')

        user = request.user
        # 存数据
        redis_conn = get_redis_connection('carts')
        # hash 用覆盖写入的方式存入数据
        redis_conn.hset('cart_%s'% user.id , sku_id , count)
        # 判断selected是否为勾选转态
        if selected:
            redis_conn.sadd('selected_%s'% user.id , sku_id)
        else:
            redis_conn.srem('selected_%s'% user.id , sku_id)
        cart_sku = {
                'id': sku.id,
                'count': count,
                "selected": selected,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': settings.STATIC_URL + 'images/goods' + sku.default_image.url + '.jpg',
                'amount': sku.price * count
        }
        return  JsonResponse({'code':RETCODE.OK , 'errmsg':'OK' , 'cart_sku':cart_sku})

    def delete(self , request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 校验数据
        try:
            SKU.objects.get(id=sku_id)
        except Exception:
            return HttpResponseForbidden('参数sku_id有误')

        # 到redis缓存中删除对应的数据
        user = request.user
        redis_conn = get_redis_connection('carts')
        redis_conn.hdel('cart_%s' % user.id , sku_id)
        redis_conn.srem('selected_%s' % user.id , sku_id)

        return JsonResponse({'code':RETCODE.OK , 'errmsg':'OK'})

class CartsSelectAllView(LoginRequiredJsonMixin , View):
    def put(self , request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected')

        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected错误')

        user = request.user
        redis_conn = get_redis_connection('carts')
        # 获取到购物车中所有商品的编号
        redis_cart = redis_conn.hgetall('cart_%s'%user.id)
        redis_sku_id = redis_cart.keys()

        if selected:
            redis_conn.sadd('selected_%s' %user.id , *redis_sku_id)
        else:
            for sku_id in redis_sku_id:
                redis_conn.srem('selected_%s' % user.id, sku_id)

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})