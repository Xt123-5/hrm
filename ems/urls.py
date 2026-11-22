"""
URL configuration for ems project.
"""
from django.contrib import admin as django_admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.views.static import serve
from app01.views import depart, user
from app01.views import admin as admin_view
from app01.views import account
from app01.views import code as code_view
from app01.views import task
from app01.views import attendance
from app01.views import salary
from app01.views import notice
from app01.views import dashboard
from app01.views import ai
from app01.views import order

urlpatterns = [
    path('django-admin/', django_admin.site.urls),

    # 媒体文件（头像上传）
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # 根路径 - 根据角色跳转不同首页
    re_path(r'^$', account.index),

    # 部门管理
    path('depart/list/', depart.depart_list, name='depart_list'),
    path('depart/add/', depart.depart_add, name='depart_add'),
    path('depart/<int:nid>/edit/', depart.depart_edit, name='depart_edit'),
    path('depart/<int:nid>/delete/', depart.depart_delete, name='depart_delete'),
    path('depart/multi/', depart.depart_multi, name='depart_multi'),

    # 用户管理
    path('user/list/', user.user_list, name='user_list'),
    path('user/add/', user.user_add, name='user_add'),
    path('user/<int:nid>/edit/', user.user_edit, name='user_edit'),
    path('user/<int:nid>/delete/', user.user_delete, name='user_delete'),

    # 管理员管理
    path('admin/list/', admin_view.admin_list, name='admin_list'),
    path('admin/add/', admin_view.admin_add, name='admin_add'),
    path('admin/<int:nid>/edit/', admin_view.admin_edit, name='admin_edit'),
    path('admin/<int:nid>/delete/', admin_view.admin_delete, name='admin_delete'),
    path('admin/<int:nid>/reset/pwd/', admin_view.admin_reset_pwd, name='admin_reset_pwd'),

    # 登录/注销
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),

    # 图片验证码
    path('image/code/', code_view.check_code, name='image_code'),

    # 任务管理
    path('task/list/', task.task_list, name='task_list'),
    path('task/ajax/', task.task_ajax, name='task_ajax'),
    path('task/<int:nid>/complete/', task.task_complete, name='task_complete'),  # 员工完成任务
    path('task/<int:nid>/approve/', task.task_approve, name='task_approve'),      # 部门审批
    path('task/<int:nid>/archive/', task.task_archive, name='task_archive'),     # 超管查收归档

    # 考勤管理
    path('attendance/list/', attendance.attendance_list, name='attendance_list'),
    path('attendance/add/', attendance.attendance_add, name='attendance_add'),
    path('attendance/<int:nid>/edit/', attendance.attendance_edit, name='attendance_edit'),
    path('attendance/<int:nid>/delete/', attendance.attendance_delete, name='attendance_delete'),

    # 薪资管理
    path('salary/list/', salary.salary_list, name='salary_list'),
    path('salary/add/', salary.salary_add, name='salary_add'),
    path('salary/<int:nid>/edit/', salary.salary_edit, name='salary_edit'),
    path('salary/<int:nid>/delete/', salary.salary_delete, name='salary_delete'),

    # 公告管理
    path('notice/list/', notice.notice_list, name='notice_list'),
    path('notice/add/', notice.notice_add, name='notice_add'),
    path('notice/<int:nid>/toggle_top/', notice.notice_toggle_top, name='notice_toggle_top'),  # 切换置顶

    # 数据统计可视化（ECharts）
    path('dashboard/', dashboard.dashboard, name='dashboard'),
    path('dashboard/overview/', dashboard.overview, name='dashboard_overview'),
    path('dashboard/department_data/', dashboard.department_data, name='dashboard_dept'),
    path('dashboard/salary_trend/', dashboard.salary_trend, name='dashboard_salary'),
    path('dashboard/attendance_stats/', dashboard.attendance_stats, name='dashboard_att'),

    # 角色权限演示
    path('roles_demo/', dashboard.roles_demo, name='roles_demo'),
    # AI 智能助手
    path('ai/', ai.ai_home, name='ai_home'),
    path('ai/generate_jd/', ai.generate_jd, name='ai_generate_jd'),
    path('ai/knowledge_qa/', ai.knowledge_qa, name='ai_knowledge_qa'),
    path('ai/salary_comment/', ai.salary_comment, name='ai_salary_comment'),
    path('ai/chat/', ai.chat, name='ai_chat'),
    path('ai/chat_history/', ai.chat_history, name='ai_chat_history'),
    path('ai/data_query/', ai.data_query, name='ai_data_query'),
    path('ai/employees/', ai.ai_employees, name='ai_employees'),
    path('ai/months/', ai.ai_months, name='ai_months'),
    # 订单管理
    path('order/list/', order.order_list, name='order_list'),
    path('order/add/', order.order_add, name='order_add'),
    path('order/delete/', order.order_delete, name='order_delete'),
    path('order/detail/', order.order_detail, name='order_detail'),
    path('order/edit/', order.order_edit, name='order_edit'),
]
