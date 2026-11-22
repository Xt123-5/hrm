from django.shortcuts import render, redirect
from app01 import models


def depart_list(request):
    """部门列表"""
    # prefetch_related 优化：一次性查出每个部门的员工，避免N+1查询
    queryset = models.Department.objects.prefetch_related('userinfo_set').all()
    total_employees = models.UserInfo.objects.count()
    return render(request, "depart_list.html", {
        "queryset": queryset,
        "total_employees": total_employees,
    })


def depart_add(request):
    """新建部门"""
    if request.method == "GET":
        return render(request, "depart_add.html")

    title = request.POST.get("title")
    if title:
        models.Department.objects.create(title=title)
    return redirect("/depart/list/")


def depart_edit(request, nid):
    """编辑部门"""
    row_object = models.Department.objects.filter(id=nid).first()
    if request.method == "GET":
        return render(request, "depart_edit.html", {"row_object": row_object})

    title = request.POST.get("title")
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list/")


def depart_delete(request, nid):
    """删除部门"""
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/list/")

def depart_multi(request):
    """批量导入部门（Excel文件）"""
    from openpyxl import load_workbook

    # 1. 获取用户上传的文件对象
    file_object = request.FILES.get("exc")
    if not file_object:
        return redirect("/depart/list/")

    # 2. 用 openpyxl 读取 Excel 内容
    wb = load_workbook(file_object)
    sheet = wb.worksheets[0]

    # 3. 从第 2 行开始循环（第 1 行是表头），去重后插入
    for row in sheet.iter_rows(min_row=2):
        title = row[0].value
        if title is None:
            continue
        title = str(title).strip()
        if not title:
            continue
        if not models.Department.objects.filter(title=title).exists():
            models.Department.objects.create(title=title)

    return redirect("/depart/list/")