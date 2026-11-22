# ============================================================
# 命令：预置制度知识库数据（T3）
# 用法：python manage.py init_knowledge
# ============================================================
from django.core.management.base import BaseCommand
from app01 import models


class Command(BaseCommand):
    help = "预置公司制度知识库（考勤/请假/报销/加班/薪酬）"

    def handle(self, *args, **options):
        data = [
            {
                "title": "考勤制度",
                "content": "公司上班时间为工作日 9:00-18:00，午休 12:00-13:00。员工需按时打卡，上班时间 9:00 后未打卡视为迟到，迟到 30 分钟以上记为旷工半天；全天未打卡或未请假擅自离岗视为缺勤。缺勤扣减当日工资，迟到累计 3 次记 1 次警告。",
            },
            {
                "title": "请假制度",
                "content": "事假需提前一天在系统申请，病假需提供医院证明，年假每年 5 天需提前一周申请。请假需经部门负责人审批，未经审批擅自离岗按缺勤处理。",
            },
            {
                "title": "报销制度",
                "content": "差旅费、招待费需在发生后 30 天内提交报销，需附发票原件。单笔超过 5000 元需部门负责人审批。",
            },
            {
                "title": "加班制度",
                "content": "工作日加班按 1.5 倍工资计算，周末加班按 2 倍，法定节假日按 3 倍。加班需提前报备并经部门负责人确认。",
            },
            {
                "title": "薪酬制度",
                "content": "员工薪酬由基本工资、奖金、扣款构成，实发工资=基本工资+奖金-扣款。每月 10 日前发放上月工资。",
            },
        ]
        for item in data:
            obj, created = models.Knowledge.objects.update_or_create(
                title=item["title"], defaults={"content": item["content"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS("已创建：" + item["title"]))
            else:
                self.stdout.write("已更新：" + item["title"])
        self.stdout.write(self.style.SUCCESS("知识库预置完成"))