from django.shortcuts import render, redirect, HttpResponse
from utils.pay import AliPay
import json
import time


def get_ali_object():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info

    app_id = "2016091100483079"

    # 支付完成后，支付偷偷向这里地址发送一个post请求
    notify_url = "http://47.94.239.156/page2/"

    # 支付完成后，跳转的地址。
    return_url = "http://47.94.239.156/page2/"

    # http://47.94.239.156/page2/?total_amount=12.00
    # &timestamp=2018-03-06+12%3A22%3A53&
    # sign=NOdwPRkmY1jpkYYpmyZUR4Y7sxuMaZe6nnbhrl%2Fh3USdCfqoQ1dMO7ED%2FTHnKoZ%2BIGbudlromV5yb6J71NeZ2Tteq8Gi3%2Fb%2FaZC2CnFWOQeo7WnO50DUmJi59Dbcn7ggc3XcPcwssMgEn%2FGb%2F6lGIBBp5pLBFd7tVpoOSQoHwwd0iS%2BHBGiS69CA6aL7WWeokw1Juy9PudvBN4Wc2hgcmMiJh%2Fd74Ii7aURV%2FyWsOTKPc223WqvrZQO587y8oAg1zt8AIoB670rxr7YsV8DZYoa8LiDn%2FRLIu7uMIqpW11OiDQLD%2FCutvGu2mojCNZMfQxw1swi6UbH6CEXox3fKFw%3D%3D&trade_no=2018030621001004780200663793&sign_type=RSA2
    # &auth_app_id=2016091100483079&charset=utf-8&seller_id=2088102175075390&method=alipay.trade.page.pay.return&app_id=2016091100483079&out_trade_no=x21520310152.1253147&version=1.0

    merchant_private_key_path = "keys/app_private_2048.txt"
    alipay_public_key_path = "keys/alipay_public_2048.txt"

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


def index(request):
    return render(request, 'index.html')


def page1(request):
    # 根据当前用户的配置，生成URL，并跳转。
    money = float(request.POST.get('money'))
    alipay = get_ali_object()
    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="充气式赵俊明",  # 商品简单描述
        out_trade_no="x2" + str(time.time()),  # 用户购买的商品订单号（每次不一样） 20180301073422891
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )

    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)

    return redirect(pay_url)


def page2(request):
    alipay = get_ali_object()
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        from urllib.parse import parse_qs
        # name&age=123....
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        # post_dict有10key： 9 ，1
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        print('------------------开始------------------')
        print('POST验证', status)
        print(post_dict)
        out_trade_no = post_dict['out_trade_no']

        # 修改订单状态
        # models.Order.objects.filter(trade_no=out_trade_no).update(status=2)

        print('------------------结束------------------')
        # 修改订单状态：获取订单号

        return HttpResponse('POST返回')

    else:
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        print('==================开始==================')
        print('GET验证', status)
        print('==================结束==================')
        return HttpResponse('支付成功')
