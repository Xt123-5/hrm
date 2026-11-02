# ============================================================
# 导入模块
# ============================================================
import hashlib
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from app01 import models
from app01.utils.bootstrap import BootStrapModelForm


# ============================================================
# 用户管理的ModelForm
# ============================================================
class UserModelForm(BootStrapModelForm):
    """新建用户ModelForm：手机号正则校验"""

    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "age", "account", "create_time", "mobile", "avatar", "gender", "depart"]
        widgets = {
            "create_time": forms.DateInput(attrs={"type": "text", "id": "dt"}),
        }


class UserEditModelForm(BootStrapModelForm):
    """编辑用户ModelForm"""

    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "age", "account", "create_time", "mobile", "avatar", "gender", "depart"]
        widgets = {
            "create_time": forms.DateInput(attrs={"type": "text", "id": "dt"}),
        }


# ============================================================
# 新建靓号ModelForm
# 作用：自动生成新建靓号的表单HTML + 校验数据格式 + 查重
# ============================================================
class PrettyModelForm(BootStrapModelForm):
    """新建靓号ModelForm：手机号正则 + 钩子校验重复"""

    # ---- 自定义mobile字段：加正则校验 ----
    mobile = forms.CharField(
        label="手机号",
        # 正则：1开头，第二位3-9，后面9个数字，共11位
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    # ---- Meta内部类：绑定模型和字段 ----
    class Meta:
        model = models.PrettyNum                       # 绑定PrettyNum表
        fields = ["mobile", "price", "level", "status"]  # 显示这4个字段

    # ---- 钩子方法：Django自动调用，校验手机号是否已存在 ----
    def clean_mobile(self):
        """钩子方法：验证手机号是否已存在"""
        txt_mobile = self.cleaned_data["mobile"]       # 取校验后的手机号
        # 查数据库：这个手机号是否已存在
        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")     # 抛错误，页面显示
        return txt_mobile                              # 返回正确值


# ============================================================
# 编辑靓号ModelForm
# 和新建的区别：查重时要排除自己，不然不改手机号也会报"已存在"
# ============================================================
class PrettyEditModelForm(BootStrapModelForm):
    """编辑靓号ModelForm：手机号正则 + 钩子排除自身后校验重复"""

    # ---- 同样的正则校验 ----
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误')],
    )

    class Meta:
        model = models.PrettyNum
        fields = ["mobile", "price", "level", "status"]

    # ---- 钩子方法：排除自己后再查重 ----
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        # exclude(id=self.instance.pk)：排除当前正在编辑的这条记录
        # self.instance.pk = 正在编辑的那条靓号的ID
        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")
        return txt_mobile


# ============================================================
# 管理员相关表单
# ============================================================
def md5(pwd):
    """MD5加密密码，数据库不存明文"""
    obj = hashlib.md5()
    obj.update(pwd.encode("utf-8"))
    return obj.hexdigest()


# ============================================================
# 新建管理员表单：用户名 + 密码 + 确认密码
# ============================================================
class AdminModelForm(BootStrapModelForm):
    """新建管理员：用户名 + 密码 + 确认密码"""

    # 额外字段：确认密码（数据库里没有，只用于二次确认）
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput,       # 输入时显示圆点
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password"]
        widgets = {
            "password": forms.PasswordInput,   # 密码框也显示圆点
        }

    def clean_password(self):
        """钩子方法：密码字段校验后MD5加密"""
        pwd = self.cleaned_data["password"]
        return md5(pwd)                    # 返回加密后的密码存入数据库

    def clean(self):
        """整体校验：两次密码是否一致"""
        pwd = self.cleaned_data.get("password")            # MD5后的密码
        confirm_pwd = self.cleaned_data.get("confirm_password")  # 明文确认密码
        # 密码框本身校验失败时，不重复报不一致
        if pwd and confirm_pwd and pwd != md5(confirm_pwd):
            self.add_error("confirm_password", "两次密码不一致")
        return self.cleaned_data


# ============================================================
# 编辑管理员表单：只允许改用户名，不允许改密码
# ============================================================
class AdminEditModelForm(BootStrapModelForm):
    """编辑管理员：只允许编辑用户名"""
    class Meta:
        model = models.Admin
        fields = ["username"]              # 只显示用户名字段


# ============================================================
# 重置密码表单：新密码 + 确认密码
# ============================================================
class AdminResetPwdForm(BootStrapModelForm):
    """重置密码：新密码 + 确认密码"""

    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = models.Admin
        fields = ["password"]
        widgets = {
            "password": forms.PasswordInput,
        }

    def clean_password(self):
        """钩子方法：校验新密码不能和原密码相同，然后MD5加密"""
        pwd = self.cleaned_data["password"]
        # self.instance = 当前正在编辑的管理员记录
        # self.instance.password = 原密码的MD5值
        if md5(pwd) == self.instance.password:
            raise ValidationError("新密码不能和原密码相同")
        return md5(pwd)

    def clean(self):
        """整体校验：两次密码是否一致"""
        pwd = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_password")
        if pwd and confirm_pwd and pwd != md5(confirm_pwd):
            self.add_error("confirm_password", "两次密码不一致")
        return self.cleaned_data


# ============================================================
# 考勤表单
# ============================================================
class AttendanceModelForm(BootStrapModelForm):
    """考勤记录表单"""
    class Meta:
        model = models.Attendance
        fields = ["employee", "date", "clock_in", "clock_out"]


# ============================================================
# 薪资表单
# ============================================================
class SalaryModelForm(BootStrapModelForm):
    """薪资记录表单"""
    class Meta:
        model = models.Salary
        fields = ["employee", "month", "base", "bonus", "deduction"]


# ============================================================
# 公告表单
# ============================================================
class NoticeModelForm(BootStrapModelForm):
    """公告表单"""
    class Meta:
        model = models.Notice
        fields = ["title", "content", "is_top"]


# ============================================================
# 任务表单
# ============================================================
class TaskModelForm(BootStrapModelForm):
    """任务表单"""
    class Meta:
        model = models.Task
        fields = ["level", "title", "detail", "owner"]
