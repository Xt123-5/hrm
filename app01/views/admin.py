# ============================================================
# 导入模块
# ============================================================
from django.shortcuts import render, redirect               # render渲染模板、redirect重定向
from app01 import models                                     # 导入数据库模型
from app01.forms import AdminModelForm, AdminEditModelForm, AdminResetPwdForm  # 管理员表单类
from app01.utils.pagination import Pagination                # 通用分页组件


# ============================================================
# 管理员列表
# URL: /admin/list/
# ============================================================
def admin_list(request):
    """管理员列表页"""
    # 查询所有管理员数据
    queryset = models.Admin.objects.all()
    # 实例化分页组件，自动切片取当前页数据
    page_object = Pagination(request, queryset)
    context = {
        "queryset": page_object.page_queryset,   # 当前页的管理员数据
        "page_string": page_object.html(),       # 分页按钮HTML
    }
    return render(request, "admin_list.html", context)


# ============================================================
# 新建管理员
# URL: /admin/add/
# ============================================================
def admin_add(request):
    """新建管理员"""
    # GET请求：返回空表单给用户填写
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "change.html", {"form": form, "title": "新建管理员"})

    # POST请求：校验并保存
    form = AdminModelForm(data=request.POST)
    if form.is_valid():                    # 自动校验：用户名格式、密码MD5、两次密码一致
        form.save()                       # 校验通过，写入数据库
        return redirect("/admin/list/")    # 重定向回列表页
    # 校验失败，返回表单（带错误信息）
    return render(request, "change.html", {"form": form, "title": "新建管理员"})


# ============================================================
# 编辑管理员（只允许编辑用户名，不允许改密码）
# URL: /admin/<int:nid>/edit/
# ============================================================
def admin_edit(request, nid):
    """编辑管理员"""
    # 根据URL中的ID查出要编辑的管理员
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect("/admin/list/")

    # GET请求：用已有数据填充表单，显示当前用户名
    if request.method == "GET":
        form = AdminEditModelForm(instance=row_object)
        return render(request, "change.html", {"form": form, "title": "编辑管理员"})

    # POST请求：更新用户名
    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": "编辑管理员"})


# ============================================================
# 删除管理员
# URL: /admin/<int:nid>/delete/
# ============================================================
def admin_delete(request, nid):
    """删除管理员"""
    models.Admin.objects.filter(id=nid).delete()    # 按ID删除
    return redirect("/admin/list/")                  # 跳回列表页


# ============================================================
# 重置密码
# URL: /admin/<int:nid>/reset/pwd/
# ============================================================
def admin_reset_pwd(request, nid):
    """重置管理员密码"""
    # 查出要重置密码的管理员
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect("/admin/list/")

    # GET请求：返回空表单
    if request.method == "GET":
        form = AdminResetPwdForm(instance=row_object)
        return render(request, "change.html", {"form": form, "title": f"重置密码 - {row_object.username}"})

    # POST请求：校验新密码并更新
    form = AdminResetPwdForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 校验通过：新密码不能和原密码相同、两次密码一致
        row_object.password = form.cleaned_data["password"]  # 取MD5加密后的新密码
        row_object.save()
        return redirect("/admin/list/")
    return render(request, "change.html", {"form": form, "title": f"重置密码 - {row_object.username}"})
