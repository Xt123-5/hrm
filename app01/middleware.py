# ============================================================
# 导入模块
# ============================================================
from django.utils.deprecation import MiddlewareMixin         # Django中间件基类
from django.shortcuts import redirect                        # 重定向


# ============================================================
# 登录校验中间件
# 作用：所有请求到达视图之前统一检查是否登录，
#       不用在每个视图函数里重复写登录判断
# ============================================================
class AuthMiddleware(MiddlewareMixin):
    """登录校验中间件"""

    def process_request(self, request):
        # ---- 第0步：白名单——不需要登录就能访问的页面 ----
        # 登录页和验证码图片，没登录也能访问
        if request.path_info in ["/login/", "/image/code/"]:
            return                          # return = 放行，继续往下走

        # ---- 第1步：检查session里有没有登录信息 ----
        info_dict = request.session.get("info")
        if info_dict:
            return                          # 已登录，放行

        # ---- 第2步：没登录，跳转到登录页 ----
        return redirect("/login/")
