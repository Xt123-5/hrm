# HRM 员工管理系统（ems2）

> 基于 Django 4.2 的企业人事管理平台（课程设计项目），覆盖部门、员工、考勤、薪资、公告、任务、订单、AI 助手与数据看板，采用 RBAC 权限模型与 Ajax 前后端交互。

---

## 一、项目简介

本项目是一个面向中小企业的员工人事管理系统，围绕「人」与「事」两条主线组织功能：

- **人**：部门 → 员工档案 → 登录账号 → 角色权限
- **事**：考勤、薪资、公告、任务、订单

系统通过自定义中间件统一完成登录校验与权限拦截，视图层专注业务逻辑，模板层通过上下文变量渲染不同角色看到的菜单与按钮。

---

## 二、功能模块

| 模块 | 主要能力 | 关键路由 |
| --- | --- | --- |
| 部门管理 | 部门列表/新增/编辑/删除、批量操作 | `/depart/list/`、`/depart/add/`、`/depart/multi/` |
| 员工管理 | 员工档案增删改查、头像上传、手机号唯一约束 | `/user/list/`、`/user/add/` |
| 管理员管理 | 账号增删改、重置密码（仅超级管理员） | `/admin/list/`、`/admin/<id>/reset/pwd/` |
| 登录与验证 | 图形验证码、密码 MD5 加密、Session 会话（8 小时） | `/login/`、`/image/code/` |
| 考勤管理 | 打卡时间登记、按时/迟到/早退/缺勤/请假五种状态 | `/attendance/list/` |
| 薪资管理 | 按月维护基本工资、奖金、扣款、实发合计 | `/salary/list/` |
| 公告管理 | 发布公告、置顶切换、按时间排序 | `/notice/list/`、`/notice/<id>/toggle_top/` |
| 任务管理 | Ajax 无刷新增删改 + 三级工作流 | `/task/list/`、`/task/ajax/` |
| 数据看板 | ECharts 图表：部门人数、薪资趋势、考勤统计 | `/dashboard/` |
| AI 助手 | 岗位 JD 生成、制度知识问答、薪资点评、多轮对话、自然语言查数 | `/ai/` |
| 订单管理 | 订单号自动生成、状态流转、详情弹窗 | `/order/list/` |
| Web 安全 | 点击劫持防护、MIME 嗅探防护、XSS 过滤、Cookie HttpOnly | 见 `ems/settings.py` |

### 任务三级工作流

```
员工提交完成 ──► 待审批 ──► 部门管理员审批 ──► 已完成 ──► 超级管理员查收 ──► 已归档
                            └──► 退回 ──► 已退回（员工重新处理）
```

### 角色与权限（RBAC）

模型为「用户 → 角色 → 权限」三层，权限以 URL 粒度登记在 `Permission.url` 字段。

| 角色 | 可见范围 | 可写范围 |
| --- | --- | --- |
| 超级管理员 | 全部页面 | 全部操作，含管理员账号与重置密码 |
| 部门管理员 | 本部门数据 + 公告 | 审批任务、维护本部门员工/考勤/薪资 |
| 普通员工 | 公告、本部门信息 | 仅本人任务提交，增删改入口全部拦截 |

中间件实现要点：`WHITE_LIST` 白名单放行登录页与验证码 → Session 校验 → `prefetch_related("roles__permissions")` 一次性预加载权限，避免 N+1 查询 → 按角色名打标到 `request.is_super_admin / is_dept_admin / is_employee`，模板可直接使用。

---

## 三、技术栈

| 分类 | 选型 |
| --- | --- |
| 后端框架 | Django 4.2（Python 3.12） |
| 数据库 | MySQL 5.7 / 8.0（`PyMySQL` 作为驱动） |
| 前端 | Django 模板 + Bootstrap 3.4.1 + jQuery 3.6.0 |
| 图表 | ECharts |
| 图片处理 | Pillow（头像上传校验与存储） |
| AI 能力 | OpenAI 兼容接口（默认 SiliconFlow，模型 `THUDM/GLM-Z1-9B-0414`） |
| 日志 | `RotatingFileHandler`，10MB 滚动、保留 5 份 |

---

## 四、目录结构

```text
ems2/
├── manage.py                    # Django 管理入口
├── requirements.txt             # 依赖清单
├── README.md
├── depart.xlsx                  # 部门示例数据
├── ems/                         # 项目配置层
│   ├── settings.py              # 数据库、中间件、日志、AI、安全配置
│   ├── urls.py                  # 全站路由表（集中注册各模块视图）
│   ├── wsgi.py / asgi.py
│   └── __init__.py              # PyMySQL 安装为 MySQLdb
├── app01/                       # 业务应用
│   ├── models.py                # 11 张表的数据模型
│   ├── forms.py                 # ModelForm 表单（含 Bootstrap 样式基类）
│   ├── middleware.py            # 登录校验 + RBAC 权限中间件
│   ├── views/                   # 按模块拆分的视图
│   │   ├── account.py           # 登录 / 注销 / 首页分流
│   │   ├── depart.py            # 部门管理
│   │   ├── user.py              # 员工管理
│   │   ├── admin.py             # 管理员与重置密码
│   │   ├── attendance.py        # 考勤
│   │   ├── salary.py            # 薪资
│   │   ├── notice.py            # 公告
│   │   ├── task.py              # 任务与 Ajax 接口
│   │   ├── dashboard.py         # 看板与图表数据接口
│   │   ├── ai.py                # AI 助手接口
│   │   ├── order.py             # 订单
│   │   └── code.py              # 图形验证码
│   ├── utils/                   # 公共工具（分页、表单样式、AI 提示词）
│   ├── management/commands/     # 自定义管理命令（知识库初始化）
│   └── migrations/              # 数据库迁移（0001 ~ 0012）
├── templates/                   # 页面模板（18 个）
├── static/                      # Bootstrap / jQuery / ECharts / 样式与图片
└── logs/                        # 运行日志（不入库）
```

---

## 五、数据库设计

| 表 | 说明 | 关键字段 |
| --- | --- | --- |
| `Department` | 部门 | `title` |
| `UserInfo` | 员工档案 | `name`、`mobile`（唯一）、`avatar`、`depart`（FK） |
| `Admin` | 登录账号 | `username`、`password`（MD5）、`roles`（M2M）、`depart`、`employee` |
| `Role` | 角色 | `title`、`permissions`（M2M） |
| `Permission` | 权限点 | `title`、`url` |
| `Attendance` | 考勤 | `employee`（FK）、`date`、`clock_in/out`、`status` |
| `Salary` | 薪资 | `employee`（FK）、`month`、`base`、`bonus`、`deduction`、`total` |
| `Notice` | 公告 | `title`、`content`、`publisher`（FK）、`is_top` |
| `Task` | 任务 | `level`、`title`、`detail`、`owner`（FK）、`status` |
| `Knowledge` | 制度知识库 | `title`、`content` |
| `ChatMessage` | AI 对话记录 | `user`（FK）、`role`、`content`、`created_at` |
| `Order` | 订单 | `oid`、`title`、`price`、`status`、`admin`（FK） |

关系要点：部门与员工一对多；账号与角色多对多；角色与权限多对多；考勤、薪资、任务、订单均持有外键并配合 `on_delete` 策略控制级联行为。

---

## 六、快速开始

### 1. 环境要求

- Python 3.10+（开发环境为 3.12）
- MySQL 5.7+，已创建数据库 `ems2`（字符集建议 `utf8mb4`）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

编辑 `ems/settings.py` 中的 `DATABASES`：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ems2',
        'USER': 'root',
        'PASSWORD': '你的数据库密码',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 5,
        },
    }
}
```

> 建议改为从环境变量读取（`os.environ.get`），不要把真实密码写进仓库。

### 4. 初始化数据库

```bash
python manage.py migrate
python manage.py init_knowledge   # 可选：写入制度知识库样例数据
python manage.py createsuperuser  # 可选：Django Admin 后台账号
```

首次登录用的业务账号可先在 `/admin/add/` 页面创建，或通过 `python manage.py shell` 写入（密码需 MD5 加密后保存）。

### 5. 启动

```bash
python manage.py runserver
```

浏览器访问 <http://127.0.0.1:8000/>，根路径会按角色自动分流首页。

---

## 七、主要路由一览

| 前缀 | 功能 |
| --- | --- |
| `/` | 按角色分流（超管→看板，部门管理员→部门数据，员工→公告） |
| `/login/`、`/logout/`、`/image/code/` | 登录、注销、图形验证码（白名单放行） |
| `/depart/*` | 部门列表、新增、编辑、删除、批量操作 |
| `/user/*` | 员工列表、新增、编辑、删除 |
| `/admin/*` | 管理员管理、重置密码 |
| `/attendance/*` | 考勤登记与维护 |
| `/salary/*` | 薪资维护 |
| `/notice/*` | 公告发布与置顶 |
| `/task/*` | 任务列表、Ajax 接口、完成/审批/归档 |
| `/dashboard/*` | 看板页面与四组图表数据接口 |
| `/ai/*` | JD 生成、知识问答、薪资点评、对话与查数 |
| `/order/*` | 订单增删改查与详情 |

---

## 八、AI 助手说明

- 统一走 OpenAI 兼容的 `/chat/completions` 协议，配置项在 `ems/settings.py`：`AI_API_KEY`、`AI_BASE_URL`、`AI_MODEL`
- 能力：根据岗位信息生成 JD、基于 `Knowledge` 表的制度问答、对薪资数据生成点评、保存多轮对话到 `ChatMessage`、把自然语言问题转成数据查询
- 若未配置可用 Key，AI 接口会返回错误提示，不影响其他模块使用

---

## 九、安全与日志

| 配置 | 作用 |
| --- | --- |
| `SECURE_CONTENT_TYPE_NOSNIFF` | 禁止浏览器猜测 MIME 类型 |
| `SECURE_BROWSER_XSS_FILTER` | 开启浏览器 XSS 过滤 |
| `X_FRAME_OPTIONS = 'DENY'` | 防点击劫持 |
| `SESSION_COOKIE_HTTPONLY` | 禁止 JS 读取 Session Cookie |
| `SESSION_COOKIE_AGE = 8h` | 会话有效期 8 小时 |
| `LOGGING` | 控制台 INFO + 文件 WARNING，10MB×5 滚动 |

> 上线前必改：`SECRET_KEY` 换为随机值、`DEBUG` 置 `False`、`ALLOWED_HOSTS` 收敛为真实域名、数据库与 AI Key 迁到环境变量。

---

## 十、常见问题

**1. `django.db.utils.OperationalError: (1045, "Access denied")`**
数据库账号密码不匹配，检查 `settings.py` 的 `USER/PASSWORD`。

**2. `No module named 'MySQLdb'`**
`ems/__init__.py` 中需要 `pymysql.install_as_MySQLdb()`，并确认已安装 `PyMySQL`。

**3. 登录后一直跳回登录页**
中间件白名单之外的所有请求都要求 Session，确认登录视图里有写入 `request.session["info"]`。

**4. 中文显示为方块或乱码**
编辑器/数据库连接必须使用 UTF-8（`utf8mb4`）；`.gitignore`、`README`、源码统一按 UTF-8 保存。

**5. 静态资源 404**
开发环境保持 `DEBUG = True`，且 `STATICFILES_DIRS` 指向 `BASE_DIR / 'static'`。

---

## 十一、后续计划

- [ ] 数据库与 AI Key 改为环境变量 / `.env` 管理
- [ ] 引入 `django-environ` 与区分 dev / prod 配置
- [ ] 补充分层单元测试（模型、中间件权限、任务工作流）
- [ ] 接口层统一返回结构与异常处理
- [ ] 增加导出 Excel（考勤、薪资）能力

---

## 十二、说明

- 本项目为课程设计/学习用途，未做生产级加固，请勿直接部署到公网承载真实人事数据。
- 密码字段采用 MD5 存储以贴合课程设计实验要求；生产环境应改用 `make_password` / `check_password`（PBKDF2）。
