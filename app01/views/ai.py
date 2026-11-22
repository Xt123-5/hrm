# ============================================================
# 模块：AI 智能助手视图（基于大模型的智能员工助手）
# ============================================================
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from app01 import models
from app01.utils.ai import LLMClient
from app01.utils.prompts import (
    JD_SYSTEM, QA_SYSTEM, COMMENT_SYSTEM, CHAT_SYSTEM, build_jd_prompt,
)


def ai_home(request):
    """AI 智能助手主页。"""
    return render(request, "ai_home.html")


# 模块A：智能生成招聘 JD（T2）
@csrf_exempt
def generate_jd(request):
    title = request.POST.get("title", "").strip()
    if not title:
        return JsonResponse({"status": False, "error": "岗位名称不能为空"})
    if len(title) > 50:
        return JsonResponse({"status": False, "error": "岗位名称过长"})
    try:
        text = LLMClient.chat(build_jd_prompt(title), system=JD_SYSTEM)
        return JsonResponse({"status": True, "data": text})
    except Exception as e:
        return JsonResponse({"status": False, "error": f"生成失败：{e}"})


# 模块B：制度知识库问答（T3）
@csrf_exempt
def knowledge_qa(request):
    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"status": False, "error": "问题不能为空"})
    if len(question) > 200:
        return JsonResponse({"status": False, "error": "问题过长"})

    items = list(models.Knowledge.objects.filter(
        Q(title__icontains=question) | Q(content__icontains=question)
    ))

    if not items:
        import re
        keywords = [w for w in re.split(r'[\s，。！？、；：,.!?]+', question) if len(w) >= 2]
        q = Q()
        for kw in keywords:
            q |= Q(title__icontains=kw) | Q(content__icontains=kw)
        items = list(models.Knowledge.objects.filter(q)) if keywords else []

    if not items:
        items = list(models.Knowledge.objects.all())

    if not items:
        return JsonResponse({"status": True, "data": "不知道"})

    context = "\n".join(f"《{k.title}》\n{k.content}" for k in items[:5])
    prompt = f"【资料】\n{context}\n\n【问题】\n{question}\n\n请用简洁中文回答。"

    try:
        text = LLMClient.chat(prompt, system=QA_SYSTEM)
        return JsonResponse({"status": True, "data": text})
    except Exception as e:
        return JsonResponse({"status": False, "error": f"回答失败：{e}"})


# 模块C：数据智能点评（T4）
@csrf_exempt
def salary_comment(request):
    emp_name = request.POST.get("employee", "").strip()
    month = request.POST.get("month", "").strip()
    if not emp_name or not month:
        return JsonResponse({"status": False, "error": "请填写员工姓名和月份"})

    queryset = models.Salary.objects.select_related('employee').filter(month=month)

    if hasattr(request, 'is_dept_admin') and request.is_dept_admin:
        if request.admin_object.depart:
            queryset = queryset.filter(employee__depart=request.admin_object.depart)
        else:
            queryset = queryset.none()
    if hasattr(request, 'is_employee') and request.is_employee:
        if request.admin_object.employee:
            queryset = queryset.filter(employee_id=request.admin_object.employee.id)
        else:
            queryset = queryset.none()

    record = queryset.filter(employee__name=emp_name).first()
    if not record:
        return JsonResponse({"status": False, "error": "未找到该员工该月的薪资记录"})

    data_text = (
        f"员工{record.employee.name}，{month}月：基本工资{record.base}元，"
        f"奖金{record.bonus}元，扣款{record.deduction}元，实发{record.total}元。"
    )
    prompt = f"{data_text}\n请生成一句简短、客观的薪资点评，约30字。只输出这一句点评本身，不要附带字数标注、理由解释或\u0027解析\u0027等多余内容。"

    try:
        text = LLMClient.chat(prompt, system=COMMENT_SYSTEM)
        return JsonResponse({"status": True, "data": text})
    except Exception as e:
        return JsonResponse({"status": False, "error": f"生成失败：{e}"})


# 模块D：多轮对话助手（T5）
@csrf_exempt
def chat(request):
    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"status": False, "error": "内容不能为空"})
    if len(question) > 500:
        return JsonResponse({"status": False, "error": "内容过长"})

    admin = request.admin_object
    models.ChatMessage.objects.create(user=admin, role="user", content=question)

    history = list(
        models.ChatMessage.objects.filter(user=admin).order_by('-created_at')[:20]
    )
    history.reverse()

    messages = [{"role": "system", "content": CHAT_SYSTEM}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})

    try:
        answer = LLMClient.chat_messages(messages)
        models.ChatMessage.objects.create(user=admin, role="assistant", content=answer)
        return JsonResponse({"status": True, "data": answer})
    except Exception as e:
        return JsonResponse({"status": False, "error": f"回答失败：{e}"})


@csrf_exempt
def chat_history(request):
    admin = request.admin_object
    history = models.ChatMessage.objects.filter(user=admin).order_by('created_at')[:50]
    data = [{"role": h.role, "content": h.content} for h in history]
    return JsonResponse({"status": True, "data": data})

# 模块E：数据智能问答（悬浮球，按身份限权）
from django.db.models import Count, Sum

DATA_QUERY_SYSTEM = "你是企业智能助手，可基于提供的【数据】和【公司制度】回答。涉及人数、金额等数据时，请用模糊表述（如'十几人''二十多人''约五千元'），不要给出精确数字。没有相关信息时请回答'当前数据中没有相关信息'。"


def _salary_text(salary_qs):
    if not salary_qs.exists():
        return "薪资数据：无"
    latest = salary_qs.order_by('-month').first()
    total = salary_qs.filter(month=latest.month).aggregate(t=Sum('total'))['t'] or 0
    return f"最新月份（{latest.month}）薪资总额：{float(total)}元"


def _attendance_text(att_qs):
    if not att_qs.exists():
        return "无"
    status_map = {1: "按时", 2: "迟到", 3: "早退", 4: "缺勤", 5: "请假"}
    stats = att_qs.values('status').annotate(c=Count('id'))
    parts = [f"{status_map.get(s['status'], '未知')} {s['c']} 次" for s in stats]
    return "，".join(parts)


def _build_data_context(request):
    admin = request.admin_object
    is_super = getattr(request, 'is_super_admin', False)
    is_dept = getattr(request, 'is_dept_admin', False)
    lines = []

    if is_super:
        lines.append("角色：超级管理员（可查看全公司数据）")
        dept_parts = []
        for d in models.Department.objects.all():
            dept_parts.append(f"{d.title}（{d.userinfo_set.count()}人）")
        lines.append("部门及人数：" + ("；".join(dept_parts) or "无"))
        lines.append(f"员工总数：{models.UserInfo.objects.count()}")
        lines.append(_salary_text(models.Salary.objects.all()))
        lines.append("考勤统计：" + _attendance_text(models.Attendance.objects.all()))

    elif is_dept:
        dept = admin.depart
        lines.append("角色：部门管理员（可查看本部门数据）")
        if not dept:
            lines.append("未分配部门，无可见数据")
        else:
            lines.append(f"所属部门：{dept.title}")
            lines.append(f"部门人数：{dept.userinfo_set.count()}")
            lines.append(_salary_text(models.Salary.objects.filter(employee__depart=dept)))
            lines.append("考勤统计：" + _attendance_text(models.Attendance.objects.filter(employee__depart=dept)))

    else:
        emp = admin.employee
        lines.append("角色：普通员工（可查看自己及本部门基本信息）")
        if not emp:
            lines.append("未关联员工档案，无可见数据")
        else:
            lines.append(f"姓名：{emp.name}")
            lines.append(f"部门：{emp.depart.title if emp.depart else '无'}")
            if emp.depart:
                lines.append(f"部门人数：{emp.depart.userinfo_set.count()}")
            lines.append(f"年龄：{emp.age}，性别：{'男' if emp.gender == 1 else '女'}，手机：{emp.mobile or '无'}")
            lines.append(_salary_text(models.Salary.objects.filter(employee=emp)))
            lines.append("考勤统计：" + _attendance_text(models.Attendance.objects.filter(employee=emp)))

    return "\n".join(lines)


@csrf_exempt
def data_query(request):
    question = request.POST.get("question", "").strip()
    if not question:
        return JsonResponse({"status": False, "error": "问题不能为空"})
    if len(question) > 300:
        return JsonResponse({"status": False, "error": "问题过长"})

    context = _build_data_context(request)
    kb = "\n".join(f"《{k.title}》\n{k.content}" for k in models.Knowledge.objects.all())
    prompt = (
        f"【当前用户可见的数据】\n{context}\n\n"
        f"【公司制度】\n{kb}\n\n"
        f"【用户问题】\n{question}\n\n"
        f"请基于以上数据和制度，用简洁中文回答。"
    )
    try:
        text = LLMClient.chat(prompt, system=DATA_QUERY_SYSTEM)
        return JsonResponse({"status": True, "data": text})
    except Exception as e:
        return JsonResponse({"status": False, "error": f"回答失败：{e}"})

def _visible_employees(request):
    emp_qs = models.UserInfo.objects.all()
    if getattr(request, 'is_dept_admin', False):
        if request.admin_object.depart:
            emp_qs = emp_qs.filter(depart=request.admin_object.depart)
        else:
            emp_qs = emp_qs.none()
    elif getattr(request, 'is_employee', False):
        if request.admin_object.employee:
            emp_qs = emp_qs.filter(id=request.admin_object.employee_id)
        else:
            emp_qs = emp_qs.none()
    return emp_qs


@csrf_exempt
def ai_employees(request):
    data = [{"id": e.id, "name": e.name} for e in _visible_employees(request).order_by('id')]
    return JsonResponse({"status": True, "data": data})

@csrf_exempt
def ai_months(request):
    emp_qs = _visible_employees(request)
    months = list(models.Salary.objects.filter(employee__in=emp_qs).values_list('month', flat=True).distinct().order_by('-month'))
    return JsonResponse({"status": True, "data": months})
