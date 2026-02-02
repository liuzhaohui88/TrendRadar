# TrendRadar Nina 扩展升级文档

> 基于官方 v5.5.0 的定制扩展版本，新增 Web 管理后台和多规则精准分流功能

## 📋 版本信息

| 项目 | 版本 |
|------|------|
| 基础版本 | TrendRadar v5.5.0 |
| 扩展版本 | Nina v5.5.0 |
| 升级日期 | 2026-02-02 |

## ✨ Nina 扩展新增功能

### 1. Web 管理后台

| 功能 | 说明 |
|------|------|
| 🔐 登录认证 | Token 机制，7天有效期 |
| 📡 数据源管理 | 热榜平台 / RSS 订阅统一管理 |
| 🔑 关键词策略 | 支持必须词、排除词、优先级 |
| 📤 推送渠道 | 飞书/钉钉/Telegram 等 + 连通性测试 |
| 📋 分发规则 | **多规则精准分流** |
| 📊 仪表盘 | 统计数据、推送日志 |

### 2. 多规则精准分流（核心功能）

官方版本所有渠道收到相同内容，Nina 扩展支持：

```
规则1: AI热点 → 飞书群A
规则2: 股票资讯 → 钉钉群B
规则3: 全量新闻 → n8n处理
```

## 📁 新增文件清单

```
trendradar/
├── db/                          # 数据库模块
│   ├── __init__.py
│   ├── database.py              # SQLModel 引擎
│   └── models.py                # 6个表模型
└── api/                         # API 模块
    ├── __init__.py
    ├── app.py                   # FastAPI + Token 认证
    └── routes/
        ├── __init__.py
        ├── sources.py           # 数据源 CRUD
        ├── keywords.py          # 关键词策略 CRUD
        ├── channels.py          # 推送渠道 CRUD + 测试
        ├── rules.py             # 分发规则 CRUD + 测试
        ├── dashboard.py         # 仪表盘统计
        └── news.py              # 新闻查询

frontend/                        # Vue3 前端
├── package.json
├── vite.config.ts
├── index.html
└── src/
    ├── main.ts, App.vue
    ├── router/index.ts          # 路由 + 登录守卫
    ├── utils/request.ts         # Axios 封装
    ├── layout/MainLayout.vue    # 主布局
    └── views/                   # 6个管理页面
        ├── Login.vue
        ├── Dashboard.vue
        ├── Sources.vue
        ├── Keywords.vue
        ├── Channels.vue
        ├── Rules.vue
        └── News.vue
```

## 🚀 本地开发

### 启动后端

```bash
cd /path/to/TrendRadar
uv sync
uv run uvicorn trendradar.api.app:app --reload --port 8000
```

### 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

### 访问

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- 登录凭证：`admin` / `trendradar`

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t trendradar-nina:5.5.0 .
```

### 运行容器

```bash
docker run -d \
  --name trendradar-nina \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  -e ADMIN_USER=admin \
  -e ADMIN_PASSWORD=your_password \
  -e TZ=Asia/Shanghai \
  trendradar-nina:5.5.0
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ADMIN_USER` | 管理员账号 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `trendradar` |
| `TZ` | 时区 | `Asia/Shanghai` |

## 🔄 与官方版本同步

本扩展采用模块化设计，不修改官方核心代码：

```bash
# 添加上游仓库
git remote add upstream https://github.com/sansan0/TrendRadar.git

# 同步官方更新
git fetch upstream
git checkout master
git merge upstream/master

# 合并到 nina 分支
git checkout 5.5_nina
git merge master
```

## 📊 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    官方 v5.5 核心（不动）                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ config.yaml │──│ AppContext  │──│ 抓取/存储/通知   │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Nina 扩展层（定制功能）                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │ 登录认证    │  │  分发规则    │  │   Web 管理界面   │ │
│  │ (Token)    │  │ (数据库)    │  │   (Vue3)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 📝 更新日志

### v5.5.0-nina (2026-02-02)

- ✨ 新增 Web 管理后台
- ✨ 新增 Token 登录认证
- ✨ 新增多规则精准分流功能
- ✨ 新增推送渠道连通性测试
- ✨ 新增分发规则测试功能
- ✨ 新增仪表盘统计页面
- 🔧 基于官方 v5.5.0 开发

---

**维护者**: 老王 (Claude Code)
