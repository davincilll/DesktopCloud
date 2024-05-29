import logging

from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from Users.models import User

import uuid


def generate_token():
    """
    生成一个没有连字符的 UUID 作为 token。

    返回:
    str: 生成的 token。
    """
    return uuid.uuid4().hex


# Create your views here.

# 写一个 drf 邮箱注册的接口
@api_view(['POST'])
# 这里进行邮箱注册
def sendCode(request):
    # 检验邮箱是否存在
    email = request.data['email'].lower()
    # 查询邮箱是否被注册过
    if User.objects.filter(email=email).exists():
        return Response({"errcode": 1, "msg": "邮箱已被注册", "data": {}})
    # 发送邮件
    rand_str = sendMessage(email)
    # 将验证码放入缓存，有效时间是10min
    cache.set(email, rand_str, 600)
    return Response({"errcode": 0, "msg": "发送成功", "data": {"code": rand_str}})


def sendMessage(email):  # 发送邮件并返回验证码
    # todo:有时间加上限流和鉴权
    # 生成验证码
    import random
    str1 = '0123456789'
    rand_str = ''
    for i in range(0, 6):
        rand_str += str1[random.randrange(0, len(str1))]
    # 发送邮件：
    # send_mail的参数分别是  邮件标题，邮件内容，发件箱(settings.py中设置过的那个)，收件箱列表(可以发送给多个人),失败静默(若发送失败，报错提示我们)
    message = "您的验证码是" + rand_str + "，10分钟内有效，请尽快填写"
    # 这里
    emailBox = [email]
    send_mail('MyDesktopCloud', message, '3135287831@qq.com', emailBox, fail_silently=False)
    return rand_str


# 这里进行注册
@api_view(['POST'])
def register(request):
    # 进行邮箱注册
    # 获取注册邮箱
    email = request.data['email'].lower()
    # 获取邮箱验证码
    code = request.data['code']
    # 获取密码
    password = request.data['password']
    # 查询邮箱是否被注册过
    if User.objects.filter(email=email).exists():
        return Response({"errcode": 1, "msg": "邮箱已被注册", "data": {}})
    # 使用session的方式保持登录
    if cache.get(email) == code:  # 验证验证
        token = generate_token()
        User.objects.create(email=email, password=password, token=token)
        return Response({"errcode": 0, "errmsg": "注册成功", "data": {"token": token}})
    else:
        return Response({"errcode": 1, "msg": "验证码错误", "data": {}})


# cookie检验装饰器
def check_login(func):
    def inner(request, *args, **kwargs):
        next_url = request.get_full_path()
        # 假设设置的cookie的key为login，value为yes
        if request.get_signed_cookie("login", salt="SSS", default=None) == 'yes':
            # 已经登录的用户，则放行
            return func(request, *args, **kwargs)
        else:
            # 没有登录的用户，跳转到登录页面
            return Response({"errcode": 1, "msg": "请先登录", "data": {"next": next_url}},
                            status=status.HTTP_401_UNAUTHORIZED)

    return inner


# 利用账户进行登录
@api_view(['POST'])
def login(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email, password=password).first()
    if user:
        response = Response({"errcode": 0, "msg": "登录成功", "data": {}})
        response.set_signed_cookie("login", 'yes', salt="SSS", max_age=36000)
        return response
    else:
        return Response({"errcode": 1, "msg": "账号或密码错误", "data": {}})


@csrf_exempt
@api_view(['POST'])
def syncBookmarkConfig(request):
    logger = logging.getLogger(__name__)
    logger.info(request.data)
    #
    email = request.data['email'].lower()
    token = request.data['token']
    bookmarks = request.data['bookmarks']
    # 检验token的正确性
    if not User.objects.filter(email=email, token=token).exists():
        return Response({"errcode": 1, "msg": "账号或密码错误", "data": {}})
    # 更新新的json配置文件
    user = User.objects.get(email=email)
    user.bookmarkConfig = bookmarks
    user.save()

    # todo:这里需要把json信息写到数据库里去
    return Response({"errcode": 0, "msg": "成功更新书签信息", "data": {}})


# @check_login
@api_view(['POST'])
@csrf_exempt
def getBookmarkConfig(request):
    # 利用邮箱和token来获取user
    email = request.data['email'].lower()
    token = request.data['token']
    user = User.objects.filter(email=email, token=token).first()
    if user:
        return Response({"errcode": 0, "msg": "成功获取用户信息", "data": user.bookmarkConfig})
    return Response({"errcode": 0, "msg": "邮箱或token信息有误", "data": {}})
