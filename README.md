# 诗词接龙游戏项目

本项目是一个结合了诗词文化与互动娱乐的Web应用，旨在提供一个在线的诗词接龙游戏平台。用户可以注册登录，参与不同模式的诗词接龙对战（包括人机智能对战），查看排行榜，并浏览和搜索诗词库。

## 核心功能

*   **用户系统**：支持用户注册、登录与认证。
*   **诗词对战**：
    *   **普通模式**：用户根据上一句诗的末尾字接出下一句。
    *   **智能诗词接龙模式**：与AI进行对战。AI（基于智谱GLM-4大语言模型）负责出题、判断用户答案的正确性（包括首尾字和诗句真实性）并进行接龙。
*   **排行榜系统**：展示用户的对战成绩和排名。
*   **诗词库浏览**：提供诗词搜索、按作者/朝代筛选等功能。
*   **数据爬虫**：内置Python爬虫脚本，用于从外部网站抓取和扩充诗词数据库。

## 技术栈

**前端:**

*   **Vue 3:** 用于构建用户界面的渐进式 JavaScript 框架。
*   **Vite:** 下一代前端构建工具，提供极速的冷启动和热模块替换 (HMR)。
*   **Element Plus:** 基于 Vue 3 的桌面端 UI 组件库。
*   **Pinia:** Vue 的官方状态管理库。
*   **Vue Router:** Vue 的官方路由管理器。
*   **Axios:** 基于 Promise 的 HTTP 客户端，用于与后端API交互 (通过封装的 `request` 工具)。
*   **lodash-es:** 提供实用工具函数的 ES模块版本。

**后端:**

*   **Python 3.11+:** 项目主要的编程语言。
*   **FastAPI:** 高性能的现代 Python Web 框架，用于构建 API。
*   **SQLAlchemy:** SQL 工具包和对象关系映射器 (ORM)，用于数据库交互。
*   **Pydantic (v2):** 基于 Python 类型提示的数据验证和设置管理库。
*   **Uvicorn:** ASGI 服务器，用于运行 FastAPI 应用。
*   **MySQL (通过 pymysql):** 项目使用的关系型数据库。
*   **JSON Web Tokens (JWT):** 用于用户认证。
*   **ZhipuAI SDK (`zhipuai`):** 用于与智谱AI的GLM系列大语言模型进行交互。
*   **Requests, BeautifulSoup4, lxml:** 用于数据爬虫模块，实现网页内容抓取和解析。

## 项目结构概览

```
.
├── backend/                  # 后端应用 (FastAPI)
│   ├── app/
│   │   ├── api/              # API路由模块 (endpoints)
│   │   ├── core/             # 核心配置 (config.py, database.py)
│   │   ├── crud/             # 数据库CRUD操作 (Create, Read, Update, Delete)
│   │   ├── llm_service/      # 大语言模型服务 (llm_service.py)
│   │   ├── models/           # SQLAlchemy数据库模型 (models.py)
│   │   ├── schemas/          # Pydantic数据校验模型
│   │   └── main.py           # FastAPI应用主入口
│   ├── data/                 # (可选) 存放爬虫的临时数据或输出
│   ├── .env.example          # 环境变量示例文件
│   ├── requirements.txt      # 后端Python依赖
│   └── spider.py             # 数据爬虫脚本
├── frontend/                 # 前端应用 (Vue 3)
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── assets/           # 静态资源 (图片、样式等)
│   │   ├── components/       # 可复用的Vue组件
│   │   ├── router/           # Vue Router路由配置
│   │   ├── store/            # Pinia状态管理
│   │   ├── utils/            # 工具函数
│   │   └── views/            # 页面级组件
│   ├── public/               # Vite的公共资源文件夹
│   ├── index.html            # 入口HTML文件
│   └── package.json          # 前端项目配置和依赖
├── poetry_battle.sql         # 数据库初始化SQL文件 (表结构和部分初始数据)
└── README.md                 # 本文档
```

## 安装与运行

### 1. 环境准备

*   **Node.js:** (建议版本 16.x 或更高) 用于运行前端项目。
*   **Python:** (建议版本 3.11 或更高) 用于运行后端项目。
*   **MySQL:** (建议版本 5.7 或更高) 关系型数据库。

### 2. 克隆项目

```bash
git clone [项目地址] # 请替换为实际的项目git仓库地址
cd [项目目录]     # 进入项目根目录
```

### 3. 后端配置与启动

#### a. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

#### b. 配置环境变量

在 `backend` 目录下，复制 `.env.example` 文件并重命名为 `.env`:

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入必要的配置信息：

```dotenv
# 数据库连接信息
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user      # 替换为你的MySQL用户名
MYSQL_PASSWORD=your_mysql_password # 替换为你的MySQL密码
MYSQL_DB=poetry_battle          # 数据库名，与 poetry_battle.sql 对应

# 大语言模型API Key (用于智能诗词接龙)
LLM_API_KEY="YOUR_ZHIPU_API_KEY"  # 替换为你的智谱AI API Key

# JWT 密钥 (用于用户认证)
JWT_SECRET_KEY="your_strong_secret_key" # 建议替换为一个强随机字符串
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

#### c. 初始化数据库

1.  确保你的MySQL服务已启动。
2.  创建一个名为 `poetry_battle` 的数据库（如果 `.env` 中 `MYSQL_DB` 使用的是其他名称，请对应修改）。
3.  导入项目根目录下的 `poetry_battle.sql` 文件到你创建的数据库中。这会创建所需的表并导入一些初始诗词数据。
    *   你可以使用MySQL客户端工具（如phpMyAdmin, Navicat, DBeaver等）或命令行执行此操作。
    *   例如，使用 `mysql` 命令行工具：
        ```bash
        mysql -u your_mysql_user -p poetry_battle < ../poetry_battle.sql
        ```
        (在 `backend` 目录下执行此命令，并根据提示输入MySQL密码)

#### d. 启动后端开发服务器

在 `backend` 目录下运行：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，API将在 `http://localhost:8000` 上可用。你可以通过访问 `http://localhost:8000/docs` 查看Swagger UI自动生成的API文档。

### 4. 前端配置与启动

#### a. 安装Node.js依赖

```bash
cd frontend  # 如果不在frontend目录，请先切换
npm install
```

#### b. 运行前端开发服务器

```bash
npm run dev
```

前端开发服务器通常会运行在 `http://localhost:5173` (Vite默认) 或其他指定端口。请留意控制台输出的实际访问地址。

### 5. 数据爬虫 (`spider.py`)

`spider.py` 脚本用于从 `gushici.china.com` 网站爬取诗词数据并存入数据库，以扩充诗词库。

#### a. 运行爬虫

确保后端环境已配置正确（特别是数据库连接）。在 `backend` 目录下运行：

```bash
python spider.py
```

#### b. 爬虫配置

你可以直接修改 `spider.py` 文件中的以下变量来控制爬取行为：

*   `max_pages_to_crawl`: 想要爬取的总页数。
*   `start_page`: 从第几页开始爬取（默认为1）。
*   `consecutive_empty_pages_limit`: 当连续多少个页面没有爬取到新诗歌时自动停止（用于处理已存在数据或到达末页的情况）。

**注意：** 大规模爬取数据可能非常耗时，并可能对目标服务器造成压力。请合理设置爬取页数和频率，并遵守目标网站的 `robots.txt`（如果有）。

## 功能使用简介

### 1. 用户注册和登录
- 访问前端应用首页，通常会有"注册"和"登录"入口。
- 按照提示完成注册和登录操作。

### 2. 诗词对战

#### a. 普通模式
- 选择普通对战模式。
- 系统给出开头的诗句。
- 用户根据上一句的最后一个字，输入下一句诗（必须是真实存在的诗句）。
- 系统判断是否符合接龙规则。

#### b. 智能诗词接龙模式
- 选择智能对战模式。
- AI（智谱GLM-4）会给出第一句诗。
- 用户根据AI的诗句进行接龙，输入下一句诗。
- AI会判断用户答案：
    - **首尾字是否匹配**。
    - **诗句是否真实存在**（通过查询数据库）。
- 如果用户回答正确，AI会接着用户的诗句再进行接龙，给出新的诗句。
- 如此循环进行，直到一方无法接上。

### 3. 查看排行榜
- 应用内通常有"排行榜"页面，展示不同维度（如胜场、积分等）的用户排名。

### 4. 浏览诗词库
- 应用内提供诗词库的浏览和搜索功能。
- 可能支持按作者、朝代、关键词等进行筛选和查找。

## 开发计划 (示例)

- [x] 实现基础用户注册与登录
- [x] 实现普通诗词对战模式
- [x] 实现智能诗词接龙模式 (AI出题、判断、接龙)
- [x] 实现诗词数据爬虫及数据库存储
- [ ] 优化对战匹配算法和排行榜逻辑
- [ ] 增加多人在线对战模式
- [ ] 丰富诗词学习与赏析功能
- [ ] 提升前端用户体验和移动端适配
- [ ] 完善爬虫功能，支持更多数据源和更灵活的爬取策略
- [ ] 增加单元测试和集成测试

## 贡献指南

欢迎对本项目做出贡献！

1.  Fork 本项目仓库。
2.  基于 `main` 或 `develop` 分支创建一个新的特性分支 (e.g., `feature/your-new-feature` or `fix/issue-number`)。
3.  在你的分支上进行修改和开发。
4.  确保你的代码符合项目的编码规范（如果项目有定义的话）。
5.  提交你的更改 (Commit your changes)。
6.  将你的分支推送到你的 Fork 仓库 (Push to the branch)。
7.  创建一个 Pull Request 到原始项目的对应分支，并清晰描述你的更改内容和目的。

## 许可证

本项目采用 [MIT License](LICENSE) (如果项目根目录有 LICENSE 文件，请确保此链接正确，否则可以移除此句或添加实际的许可证类型)。 