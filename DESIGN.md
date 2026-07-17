# 个人博客系统 — 设计方案

## 技术栈

| 层 | 选型 |
|----|------|
| 后端框架 | FastAPI (Python) |
| ORM | SQLModel |
| 数据库 | MySQL |
| 前端框架 | Vue 3 + TypeScript |
| 样式方案 | 原生 Scoped CSS |
| 状态管理 | Pinia |
| 构建工具 | Vite |
| Markdown 渲染 | 后端 mistune / 前端 marked + highlight.js |
| 认证 | JWT (python-jose) |
| 部署 | Docker Compose (Nginx + FastAPI + MySQL) |

## 功能范围（MVP）

### 前台（访客）

- 文章列表页 — 分页、按时间倒序
- 文章详情页 — Markdown 渲染、代码高亮、评论区
- 分类筛选 — 侧边栏按分类查看文章
- 标签筛选 — 侧边栏按标签查看文章
- 游客评论 — 输入昵称+邮箱+内容直接发表，无需审核，博主可删
- 侧边栏 — 个人信息、公告、最新文章、分类、标签云
- 关于页面

### 后台（博主独用）

- 登录 — 账号密码，JWT 认证
- 文章管理 — 列表 + 新建/编辑/删除，Markdown 编辑器
- 评论管理 — 列表 + 删除
- 分类/标签管理 — 增删改

### 暂不包含（后续按需加）

- RSS、搜索、阅读量统计、闪存/说说
- 多用户/注册、富文本编辑器

---

## 项目结构

```
Blog/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── public/           # 公开接口
│   │   │   │   ├── articles.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── tags.py
│   │   │   │   └── comments.py
│   │   │   └── admin/            # 后台接口（需 JWT）
│   │   │       ├── auth.py
│   │   │       ├── articles.py
│   │   │       ├── categories.py
│   │   │       ├── tags.py
│   │   │       └── comments.py
│   │   ├── models/               # SQLModel 数据模型
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── tag.py
│   │   │   ├── article.py
│   │   │   └── comment.py
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── services/             # 业务逻辑
│   │   ├── core/
│   │   │   ├── config.py         # 配置（数据库、JWT 密钥等）
│   │   │   ├── security.py       # JWT 生成/验证、密码哈希
│   │   │   └── deps.py           # 依赖注入
│   │   └── main.py               # 应用入口
│   ├── seed.py                   # 种子数据脚本
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── HomeView.vue       # 首页：文章列表 + 侧边栏
│   │   │   ├── ArticleView.vue    # 文章详情 + 评论区
│   │   │   ├── CategoryView.vue   # 分类文章列表
│   │   │   ├── TagView.vue        # 标签文章列表
│   │   │   ├── AboutView.vue      # 关于页面
│   │   │   └── admin/
│   │   │       ├── LoginView.vue
│   │   │       ├── DashboardView.vue
│   │   │       ├── ArticlesManage.vue
│   │   │       ├── ArticleEditor.vue
│   │   │       ├── CommentsManage.vue
│   │   │       ├── CategoriesManage.vue
│   │   │       └── TagsManage.vue
│   │   ├── components/
│   │   │   ├── AppHeader.vue      # 顶部导航
│   │   │   ├── AppFooter.vue      # 底部
│   │   │   ├── Sidebar.vue        # 侧边栏
│   │   │   ├── CommentSection.vue # 评论区
│   │   │   ├── Pagination.vue     # 分页
│   │   │   ├── ArticleCard.vue    # 文章卡片
│   │   │   └── MarkdownEditor.vue # 分栏编辑器
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── stores/
│   │   │   └── auth.ts            # 认证状态
│   │   ├── api/
│   │   │   └── index.ts           # Axios 封装 + 接口函数
│   │   └── App.vue
│   ├── nginx.conf
│   └── package.json
└── docker-compose.yml
```

---

## 数据库表设计

### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | |
| username | VARCHAR(50) UNIQUE NOT NULL | 登录用户名 |
| password_hash | VARCHAR(255) NOT NULL | bcrypt 哈希 |
| created_at | DATETIME | |

### categories
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | |
| name | VARCHAR(50) NOT NULL | 分类名 |
| slug | VARCHAR(50) UNIQUE NOT NULL | URL 友好标识 |
| created_at | DATETIME | |

### tags
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | |
| name | VARCHAR(50) NOT NULL | 标签名 |
| slug | VARCHAR(50) UNIQUE NOT NULL | URL 友好标识 |
| created_at | DATETIME | |

### articles
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | |
| title | VARCHAR(200) NOT NULL | 标题 |
| slug | VARCHAR(200) UNIQUE NOT NULL | URL 友好标识 |
| content | TEXT NOT NULL | Markdown 正文 |
| summary | VARCHAR(500) | 摘要 |
| cover_url | VARCHAR(500) | 封面图 URL |
| category_id | INT FK → categories.id | 所属分类 |
| is_published | BOOL DEFAULT TRUE | 是否公开 |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### article_tags（多对多中间表）
| 字段 | 类型 | 说明 |
|------|------|------|
| article_id | INT FK → articles.id | |
| tag_id | INT FK → tags.id | |

### comments
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | |
| article_id | INT FK → articles.id NOT NULL | 所属文章 |
| author_name | VARCHAR(50) NOT NULL | 评论者昵称 |
| author_email | VARCHAR(100) NOT NULL | 评论者邮箱 |
| content | TEXT NOT NULL | 评论内容 |
| is_visible | BOOL DEFAULT TRUE | 是否可见（博主可设为不可见即删除） |
| created_at | DATETIME | |

---

## API 设计

### 公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/articles` | 文章列表（分页 `?page=&page_size=`，可选 `?category_slug=&tag_slug=`） |
| GET | `/api/articles/{slug}` | 文章详情 |
| GET | `/api/categories` | 分类列表 |
| GET | `/api/tags` | 标签列表 |
| GET | `/api/comments?article_id=` | 某文章评论列表 |
| POST | `/api/comments` | 游客发表评论 |

### 后台接口（需 JWT Authorization header）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 登录，返回 access_token |
| GET | `/api/admin/articles` | 文章管理列表 |
| POST | `/api/admin/articles` | 新建文章 |
| PUT | `/api/admin/articles/{id}` | 编辑文章 |
| DELETE | `/api/admin/articles/{id}` | 删除文章 |
| GET | `/api/admin/categories` | 分类列表 |
| POST | `/api/admin/categories` | 新建分类 |
| PUT | `/api/admin/categories/{id}` | 编辑分类 |
| DELETE | `/api/admin/categories/{id}` | 删除分类 |
| GET | `/api/admin/tags` | 标签列表 |
| POST | `/api/admin/tags` | 新建标签 |
| PUT | `/api/admin/tags/{id}` | 编辑标签 |
| DELETE | `/api/admin/tags/{id}` | 删除标签 |
| GET | `/api/admin/comments` | 评论列表（所有文章） |
| DELETE | `/api/admin/comments/{id}` | 删除评论（软删除，设置 is_visible=false） |

---

## 前端路由

| 路由 | 页面组件 | 说明 |
|------|----------|------|
| `/` | HomeView | 文章列表 + 分页 + 侧边栏 |
| `/article/:slug` | ArticleView | 文章详情 + 评论区 |
| `/category/:slug` | CategoryView | 分类文章列表 |
| `/tag/:slug` | TagView | 标签文章列表 |
| `/about` | AboutView | 关于页面 |
| `/admin/login` | LoginView | 后台登录 |
| `/admin` | DashboardView | 后台首页 |
| `/admin/articles` | ArticlesManage | 文章管理列表 |
| `/admin/articles/new` | ArticleEditor | 新建文章 |
| `/admin/articles/:id/edit` | ArticleEditor | 编辑文章 |
| `/admin/comments` | CommentsManage | 评论管理 |
| `/admin/categories` | CategoriesManage | 分类管理 |
| `/admin/tags` | TagsManage | 标签管理 |

---

## 实施步骤（按依赖顺序）

### Step 1：项目脚手架 & 基础设施

- 清理现有 `main.py`、`venv/`、`__pycache__/`
- 创建 `backend/` 目录及所有空模块文件
- `requirements.txt`：fastapi, uvicorn[standard], sqlmodel, pymysql, python-jose[cryptography], passlib[bcrypt], python-multipart, mistune
- FastAPI 入口 `main.py`：app 实例、CORS 配置
- `core/config.py`：Settings 类（读取环境变量）、`core/security.py`：JWT+密码工具、`core/deps.py`：get_db, get_current_user
- 用 `npm create vue@latest frontend` 创建项目，选 TS、Vue Router、Pinia
- 配置 axios 实例 + 路由骨架

### Step 2：数据库模型

- 创建所有 SQLModel 模型（单表一个文件）
- 应用启动时 `SQLModel.metadata.create_all()` 自动建表

### Step 3：后端 API

- Schemas 层 → Services 层 → API 路由层，按先公开后后台的顺序实现
- 后台接口通过 `get_current_user` 依赖校验 JWT

### Step 4：前端页面

- 组件 → 页面 → 路由，按先前台后后台的顺序实现
- 路由守卫：`/admin/*` 检查 token，无 token 跳转登录

### Step 5：种子数据

- `seed.py` 创建一个管理员用户、一个示例分类、一篇示例文章

### Step 6：Docker 部署

- `docker-compose.yml`：MySQL + FastAPI + Nginx
- `frontend/nginx.conf`：静态文件 + API 反向代理
- `backend/Dockerfile`、前端构建多阶段 Dockerfile

---

## 关键设计决策

- **文章路由用 slug 而非 id**：SEO 友好，URL 可读
- **评论软删除**：`is_visible=false`，不物理删除数据
- **前端 Markdown 渲染用 marked + highlight.js**：轻量，CDN 引入即可
- **分页**：前端传 page + page_size，后端返回 total 总数用于计算总页数
- **JWT 存 localStorage**：简单直接，退出时清除
- **分类/标签 slug**：由 name 自动生成（小写 + 空格转连字符 + 中文保留处理）
