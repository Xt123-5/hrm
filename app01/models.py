from django.db import models

# 部门表
class Department(models.Model):
    title = models.CharField(max_length=32, verbose_name="部门名称")

    def __str__(self):
        return self.title

# 员工表
class UserInfo(models.Model):
    name = models.CharField(max_length=16, verbose_name="姓名")
    password = models.CharField(max_length=64, verbose_name="密码")
    age = models.IntegerField(verbose_name="年龄")
    account = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="账户")
    create_time = models.DateField(verbose_name="入职时间")
    mobile = models.CharField(max_length=11, verbose_name="手机号", unique=True, default="")
    avatar = models.ImageField(verbose_name="头像", upload_to="avatar/", default="avatar/default.png")
    # 外键：关联Depart，on_delete=SET_NULL 部门删除时 depart_id置空
    depart = models.ForeignKey(
        to="Department",
        to_field="id",
        on_delete=models.CASCADE,
        verbose_name="所属部门"
    )
    # gender 1男，2女
    gender_choices = ((1, "男"), (2, "女"))
    gender = models.SmallIntegerField(choices=gender_choices, verbose_name="性别")

    def __str__(self):
        return self.name


# 靓号表
class PrettyNum(models.Model):
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    price = models.IntegerField(default=0, verbose_name="价格")

    level_choices = (
        (1, "1级"),
        (2, "2级"),
        (3, "3级"),
        (4, "4级"),
    )
    level = models.SmallIntegerField(choices=level_choices, default=1, verbose_name="级别")

    status_choices = (
        (1, "已占用"),
        (2, "未使用"),
    )
    status = models.SmallIntegerField(choices=status_choices, default=2, verbose_name="状态")

    def __str__(self):
        return self.mobile


# 管理员表
class Admin(models.Model):
    username = models.CharField(max_length=32, verbose_name="用户名")
    password = models.CharField(max_length=64, verbose_name="密码")
    roles = models.ManyToManyField(to="Role", blank=True, verbose_name="角色")

    def __str__(self):
        return self.username


# ============================================================
# RBAC权限模型
# ============================================================
class Role(models.Model):
    """角色表：超级管理员/部门管理员/普通员工"""
    title = models.CharField(max_length=32, verbose_name="角色名称")
    permissions = models.ManyToManyField(to="Permission", blank=True, verbose_name="权限")

    def __str__(self):
        return self.title


class Permission(models.Model):
    """权限表：部门列表/员工列表/薪资录入等"""
    title = models.CharField(max_length=32, verbose_name="权限名称")
    url = models.CharField(max_length=128, verbose_name="权限URL", blank=True)

    def __str__(self):
        return self.title


# ============================================================
# 考勤管理
# ============================================================
class Attendance(models.Model):
    """考勤记录：员工+日期+上下班时间+状态"""
    employee = models.ForeignKey(to="UserInfo", on_delete=models.CASCADE, verbose_name="员工")
    date = models.DateField(verbose_name="日期")
    clock_in = models.TimeField(verbose_name="上班时间", null=True, blank=True)
    clock_out = models.TimeField(verbose_name="下班时间", null=True, blank=True)

    status_choices = (
        (1, "按时"),
        (2, "迟到"),
        (3, "早退"),
        (4, "缺勤"),
    )
    status = models.SmallIntegerField(choices=status_choices, default=4, verbose_name="考勤状态")

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


# ============================================================
# 薪资管理
# ============================================================
class Salary(models.Model):
    """薪资记录：员工+月份+基本工资+奖金+扣款+实发"""
    employee = models.ForeignKey(to="UserInfo", on_delete=models.CASCADE, verbose_name="员工")
    month = models.CharField(max_length=7, verbose_name="月份", help_text="格式：2026-01")
    base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="基本工资")
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="奖金")
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="扣款")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="实发工资")

    def __str__(self):
        return f"{self.employee.name} - {self.month}"


# ============================================================
# 公告管理
# ============================================================
class Notice(models.Model):
    """公告：标题+内容+发布人+发布时间+置顶"""
    title = models.CharField(max_length=64, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    publisher = models.ForeignKey(to="Admin", on_delete=models.CASCADE, verbose_name="发布人")
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    is_top = models.BooleanField(default=False, verbose_name="是否置顶")

    def __str__(self):
        return self.title


# ============================================================
# 任务管理（AJAX）
# ============================================================
class Task(models.Model):
    """任务：级别+标题+详情+负责人"""
    level_choices = (
        (1, "紧急"),
        (2, "重要"),
        (3, "普通"),
    )
    level = models.SmallIntegerField(choices=level_choices, verbose_name="级别")
    title = models.CharField(max_length=64, verbose_name="标题")
    detail = models.TextField(verbose_name="详细信息")
    owner = models.ForeignKey(to="UserInfo", on_delete=models.CASCADE, verbose_name="负责人")

    def __str__(self):
        return self.title
