# ============================================================
# 导入模块
# ============================================================
import json
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from app01 import models
from app01.forms import TaskModelForm


# ============================================================
# 任务列表页面
# URL: /task/list/
# ============================================================
def task_list(request):
    """任务列表页"""
    queryset = models.Task.objects.all()
    context = {
        "queryset": queryset,
        "owner_list": models.UserInfo.objects.all(),
    }
    return render(request, "task_list.html", context)


# ============================================================
# 任务AJAX接口
# URL: /task/ajax/
# ============================================================
@csrf_exempt
def task_ajax(request):
    """处理任务AJAX提交，返回JSON"""
    if request.method == "GET":
        data_dict = {"status": True, 'data': [11, 22, 33, 44]}
        return HttpResponse(json.dumps(data_dict))

    # POST：提交任务
    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return HttpResponse(json.dumps({"status": True, "msg": "任务添加成功"}))
    else:
        return HttpResponse(json.dumps({"status": False, "msg": form.errors}))
