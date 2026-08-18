# Enterprise Knowledge Hub Backend

企业内部知识库文档处理后端。

这是一个偏企业真实形态的后端项目，重点不是做聊天 demo，而是先把文档上传、元数据管理、异步解析、任务状态流转、chunk 产出、缓存、SSE、日志与排障这些基础能力搭起来，再在第二阶段平滑扩展最小 RAG 能力。

## 项目定位

- 面向企业内部知识库维护人员、内部工具团队和后续接入 RAG 的 AI 应用团队
- 第一阶段不接 LLM，先把后端业务底座做稳
- 按轮次生成代码，逐层补齐工程能力
- 重点训练真实业务理解、分层设计、状态流转和排障能力

## 当前进度

截至 `2026-07-31`：

- 第 1 轮已完成：项目脚手架与运行入口
- 第 2 轮已完成：数据库基础与 ORM 骨架
- 第 3 轮已完成：文档、chunk、处理任务和事件流水四个核心模型
- 已建立项目专用 Python 3.12 环境，生成 `pyproject.toml` 与 `uv.lock`
- 已开始沉浸式错误案例分析文档，当前已有第 2 轮和第 3 轮分析文件

后续会继续按 `代码生成计划.md` 推进第 4 轮及之后的内容。

## 技术栈

- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Redis
- uv
- pytest
- ruff

## 目录结构

```text
app/
  api/
  core/
  db/
  models/
  schemas/
  repositories/
  services/
  workers/
  storage/
  utils/
```

当前已经落地的核心文件包括：

- `app/main.py`
- `app/core/config.py`
- `app/core/logging.py`
- `app/core/enums.py`
- `app/core/exceptions.py`
- `app/core/auth_context.py`
- `app/api/v1/health.py`
- `app/db/base.py`
- `app/db/session.py`
- `app/models/base.py`
- `app/models/document.py`
- `app/models/document_chunk.py`
- `app/models/processing_task.py`
- `app/models/document_event.py`

## 核心设计

- `Document` 表负责文档主记录
- `ProcessingTask` 表负责解析任务
- `DocumentChunk` 表负责分段结果
- `DocumentEvent` 表负责事件流水
- Web 进程和 worker 进程分离
- PostgreSQL 作为事实来源，Redis 只做加速层
- 文档状态、任务状态、事件类型分开管理，避免把业务主状态和过程流水混在一起

## 如何启动

先安装依赖：

```powershell
uv sync
```

启动服务：

```powershell
uv run uvicorn app.main:app --reload
```

访问健康检查：

```text
http://127.0.0.1:8000/api/v1/health
```

## 开发约定

- 代码注释和文档字符串默认使用中文
- 每轮代码生成只推进当前轮次，不越轮
- 每轮代码生成后，都要补充推荐阅读顺序
- 每轮代码生成后，都要生成独立的错误案例分析文档
- 错误案例优先聚焦架构、状态流转、事务、并发和一致性问题，不刻意制造低级语法错误

## 学习与排障文档

- [`代码生成计划.md`](./代码生成计划.md)
- [`学习进度追踪.md`](./学习进度追踪.md)
- [`近期学习计划.md`](./近期学习计划.md)
- [`沉浸式错误案例分析-第2轮.md`](./沉浸式错误案例分析-第2轮.md)
- [`沉浸式错误案例分析-第3轮.md`](./沉浸式错误案例分析-第3轮.md)

## 后续补充方向

这个 README 会随着代码继续补充，后续重点会增加：

- 文档上传接口说明
- 任务查询与 SSE 接口说明
- worker 运行方式
- 数据库迁移说明
- 测试命令与验证方式
- 错误案例与排障流程

## 一句话总结

这是一个为 AI 应用开发和 Agent 开发岗位准备的企业知识库后端练习项目，目标是把“知道概念”推进到“能把项目按企业方式做出来”。
