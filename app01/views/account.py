# ============================================================
# 导入模块
# ============================================================
from django.shortcuts import render, redirect               # render渲染模板、redirect重定向
from app01 import models                                     # 导入数据库模型
import hashlib                                              # MD5加密


def md5(pwd):
    """MD5加密密码"""
    obj = hashlib.md5()
    obj.update(pwd.encode("utf-8"))
    return obj.hexdigest()


# ============================================================
# 用户登录
# URL: /login/
# ============================================================
def login(request):
    """用户登录"""
    # GET请求：返回登录页
    if request.method == "GET":
        return render(request, "login.html")

    # POST请求：取表单数据
    username = request.POST.get("username")       # 用户名
    password = request.POST.get("password")       # 明文密码
    user_code = request.POST.get("code")           # 用户输入的验证码

    # ---- 第1步：校验图片验证码 ----
    # 从session取出之前生成验证码时存的正确值
    session_code = request.session.get('image_code', '')
    # 不区分大小写比对
    if user_code.upper() != session_code.upper():
        return render(request, "login.html", {"error": "验证码错误"})

    # ---- 第2步：校验用户名密码 ----
    # 密码要MD5加密后和数据库里的加密值比对
    admin_object = models.Admin.objects.filter(
        username=username,
        password=md5(password)
    ).first()
    if not admin_object:
        return render(request, "login.html", {"error": "用户名或密码错误"})

    # ---- 第3步：登录成功，写入session ----
    # session里存用户ID和用户名，后续中间件和页面用
    request.session["info"] = {
        "id": admin_object.id,
        "name": admin_object.username
    }
    return redirect("/admin/list/")


# ============================================================
# 注销
# URL: /logout/
# ============================================================
def logout(request):
    """注销：清除session，跳回登录页"""
    request.session.clear()          # 清除所有session数据
    return redirect("/login/")       # 跳回登录页
