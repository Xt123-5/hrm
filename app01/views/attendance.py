# ============================================================
# 导入模块
# ============================================================
from django.shortcuts import render, redirect
from app01 import models
from app01.forms import AttendanceModelForm
from app01.utils.pagination import Pagination
from datetime import datetime


# ============================================================
# 考勤列表
# URL: /attendance/list/
# ============================================================
def attendance_list(request):
    """考勤列表"""
    queryset = models.Attendance.objects.all()
    page_object = Pagination(request, queryset)
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
    }
    return render(request, "attendance_list.html", context)


# ============================================================
# 新建考勤
# URL: /attendance/add/
# ============================================================
def attendance_add(request):
    """新建考勤：自动计算考勤状态"""
    if request.method == "GET":
        form = AttendanceModelForm()
        return render(request, "change.html", {"form": form, "title": "新建考勤"})

    form = AttendanceModelForm(data=request.POST)
    if form.is_valid():
        # 自动计算考勤状态
        data = form.cleaned_data
        clock_in = data.get("clock_in")
        clock_out = data.get("clock_out")

        if not clock_in or not clock_out:
            data["status"] = 4  # 缺勤
        else:
            # 9点后算迟到，18点前算早退
            late = datetime.strptime("09:00", "%H:%M").time()
            early_leave = datetime.strptime("18:00", "%H:%M").time()
            if clock_in > late and clock_out < early_leave:
                data["status"] = 2  # 迟到（早退单独算）
            elif clock_in > late:
                data["status"] = 2  # 迟到
            elif clock_out < early_leave:
                data["status"] = 3  # 早退
            else:
                data["status"] = 1  # 按时

        form.save()
        return redirect("/attendance/list/")
    return render(request, "change.html", {"form": form, "title": "新建考勤"})
