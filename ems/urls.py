"""
URL configuration for ems project.
"""
from django.contrib import admin as django_admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.views.static import serve
from app01.views import depart, user, pretty
from app01.views import admin as admin_view
from app01.views import account
from app01.views import code as code_view
from app01.views import task
from app01.views import attendance
from app01.views import salary
from app01.views import notice

urlpatterns = [
    path('django-admin/', django_admin.site.urls),

    # 媒体文件（头像上传）
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # 根路径重定向到部门列表
    re_path(r'^$', RedirectView.as_view(url='/depart/list/')),

    # 部门管理
    path('depart/list/', depart.depart_list, name='depart_list'),
    path('depart/add/', depart.depart_add, name='depart_add'),
    path('depart/<int:nid>/edit/', depart.depart_edit, name='depart_edit'),
    path('depart/<int:nid>/delete/', depart.depart_delete, name='depart_delete'),

    # 用户管理
    path('user/list/', user.user_list, name='user_list'),
    path('user/add/', user.user_add, name='user_add'),
    path('user/<int:nid>/edit/', user.user_edit, name='user_edit'),
    path('user/<int:nid>/delete/', user.user_delete, name='user_delete'),

    # 靓号管理
    path('pretty/list/', pretty.pretty_list, name='pretty_list'),
    path('pretty/add/', pretty.pretty_add, name='pretty_add'),
    path('pretty/<int:nid>/edit/', pretty.pretty_edit, name='pretty_edit'),
    path('pretty/<int:nid>/delete/', pretty.pretty_delete, name='pretty_delete'),

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

    # Ajax学习
    path('task/list/', task.task_list, name='task_list'),
    path('task/ajax/', task.task_ajax, name='task_ajax'),

    # 考勤管理
    path('attendance/list/', attendance.attendance_list, name='attendance_list'),
    path('attendance/add/', attendance.attendance_add, name='attendance_add'),

    # 薪资管理
    path('salary/list/', salary.salary_list, name='salary_list'),
    path('salary/add/', salary.salary_add, name='salary_add'),

    # 公告管理
    path('notice/list/', notice.notice_list, name='notice_list'),
    path('notice/add/', notice.notice_add, name='notice_add'),
]
