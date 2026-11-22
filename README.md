# HRM 员工管理系统（ems2）

基于 Django 的员工人事管理系统（课程设计），覆盖部门、员工、考勤、薪资、公告、任务等模块，包含 Ajax 交互与 RBAC 权限控制。

## 功能模块

- **部门管理**：部门信息维护、部门负责人设置
- **员工管理**：员工档案、入职与离职、员工与部门关联
- **考勤管理**：考勤登记与状态统计
- **薪资管理**：薪资条目维护与查询
- **公告管理**：公告发布与展示
- **任务管理**：任务下发与状态流转
- **账号与权限**：登录、中间件鉴权、基于角色的访问控制（RBAC）

## 技术栈

- Python 3.12 / Django
- MySQL（数据库配置见 `ems/settings.py`）
- 前端：Bootstrap 3.4.1 + jQuery 3.6.0 + Django 模板
- 静态资源在 `static/`，模板在 `templates/`

## 本地运行

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

浏览器访问 http://127.0.0.1:8000/

## 目录结构

```
ems2/
├── manage.py            # Django 入口
├── requirements.txt
├── ems/                 # 项目配置（settings / urls / wsgi）
├── app01/               # 业务应用
│   ├── models.py        # 数据模型
│   ├── views/           # 各模块视图
│   ├── forms.py
│   ├── middleware.py    # 登录与权限中间件
│   ├── migrations/
│   └── utils/           # 分页、初始化等工具
├── templates/           # 页面模板
├── static/              # 静态资源
└── depart.xlsx          # 部门示例数据
```

## 说明

仓库通过 `.gitignore` 排除了 `__pycache__`、IDE 配置、日志与本地数据库文件。
