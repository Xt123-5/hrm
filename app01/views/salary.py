# ============================================================
# 导入模块
# ============================================================
from django.shortcuts import render, redirect
from app01 import models
from app01.forms import SalaryModelForm
from app01.utils.pagination import Pagination


# ============================================================
# 薪资列表
# URL: /salary/list/
# ============================================================
def salary_list(request):
    """薪资列表：支持按月份/员工筛选，统计薪资总额"""
    # 筛选条件
    search_month = request.GET.get("month", "")
    search_employee = request.GET.get("employee", "")

    queryset = models.Salary.objects.all()
    if search_month:
        queryset = queryset.filter(month=search_month)
    if search_employee:
        queryset = queryset.filter(employee_id=search_employee)

    # 统计选定月份薪资总额
    total_sum = queryset.aggregate(total=__import__('django').db.models.Sum('total'))['total'] or 0

    page_object = Pagination(request, queryset)
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
        "total_sum": total_sum,
        "search_month": search_month,
        "search_employee": search_employee,
        "employee_list": models.UserInfo.objects.all(),
    }
    return render(request, "salary_list.html", context)


# ============================================================
# 新建薪资
# URL: /salary/add/
# ============================================================
def salary_add(request):
    """新建薪资：自动计算实发=基本+奖金-扣款"""
    if request.method == "GET":
        form = SalaryModelForm()
        return render(request, "change.html", {"form": form, "title": "新建薪资"})

    form = SalaryModelForm(data=request.POST)
    if form.is_valid():
        # 自动计算实发工资
        data = form.cleaned_data
        data["total"] = data["base"] + data["bonus"] - data["deduction"]
        form.save()
        return redirect("/salary/list/")
    return render(request, "change.html", {"form": form, "title": "新建薪资"})
