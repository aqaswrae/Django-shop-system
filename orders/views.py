from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU
import json
from django.http import HttpResponseForbidden , JsonResponse
from orders.models import OrderInfo , OrderGoods
from django.db import transaction
from django.utils import timezone
from utils.response_code import RETCODE

class OrdersSettlementView(LoginRequiredMixin , View):
    # 结算订单
    def get(self , request):

        # 获取用户对象
        user = request.user
        # 获得用户的收货地址
        try:
            addresses = Address.objects.filter(user=user , is_deleted=False)
        except Exception:
            addresses = None

        redis_conn = get_redis_connection('carts')
        # 获取购物车的所有商品数据
        redis_cart = redis_conn.hgetall('cart_%s' %user.id)
        # 获取勾选状态的数据
        redis_selected = redis_conn.smembers('selected_%s' %user.id)
        # 获取勾选状态的商品数据
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        # 获取商品的总件数和总金额
        total_count = 0
        total_amount = 0
        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            total_count += sku.count
            total_amount += sku.amount

        # 运费
        freight = 20
        context = {
            'skus':skus,
            'addresses':addresses,
            'total_count':total_count,
            'total_amount':total_amount,
            'freight':freight,
            # 实付金额
            'payment_amount': total_amount + freight
        }

        return render(request , 'place_order.html' , context=context)

class OrderCommitView(LoginRequiredMixin , View):
    # 提交订单
    def post(self , request):
        # {"address_id":1,"pay_method":2}
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验
        try:
            address = Address.objects.get(id = address_id)
        except Exception:
            return  HttpResponseForbidden('参数address_id有误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'] , OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseForbidden('参数pay_method有误')

        # 事务要么全部执行 ， 要么全部都不执行
        # 开启事务
        with transaction.atomic():
            # 保存数据库最初的状态
            save_id = transaction.savepoint()

            try:
                # 保存订单信息
                user = request.user
                # 订单编号
                order_id = timezone.localdate().strftime('%Y%m%d%H%M%S')+('%05d'%user.id)
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=0,
                    freight=20,
                    pay_method=pay_method,
                    # 返回值 if 判断表达式 else else的返回值
                    status= OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                            else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从缓存中取出购物车商品信息
                redis_conn = get_redis_connection('carts')
                # 获取购物车的所有商品数据
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                # 获取勾选状态的数据
                redis_selected = redis_conn.smembers('selected_%s' % user.id)
                # 获取勾选状态的商品数据
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

                sku_ids = new_cart_dict.keys()
                for sku_id in sku_ids:
                    # 获取每个商品的对象
                    sku = SKU.objects.get(id=sku_id)
                    sku_count = new_cart_dict[sku.id]

                    # 获取到商品的原始的销量和库存
                    origin_stock = sku.stock
                    origin_sales = sku.sales

                    # 判断商品购买数量是否大于库存
                    if sku_count > origin_stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code':RETCODE.STOCKERR , 'errmsg':'库存不足'})

                    # 销量和库存对应的增加或者减少
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()

                    # 保存订单商品数据
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )

                    order.total_count += sku_count
                    order.total_amount += sku_count * sku.price

                # 计算订单总金额
                order.total_amount += order.freight
                order.save()

            except Exception:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code':RETCODE.DBERR , 'errmsg':'下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        return JsonResponse({'code':RETCODE.OK,'errmsg':'OK','order_id':order_id})

class OrderSuccessView(View):
    def get(self , request):
        return render(request , 'order_success.html')








