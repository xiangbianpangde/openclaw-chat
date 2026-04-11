# Web 服务技术方案

**任务编号：** JJC-20260409-001-Web  
**研拟部门：** 中书省  
**研拟日期：** 天启二年四月十三日（2026 年 4 月 13 日）  
**版本：** v1.0

---

## 📖 技术架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  Web UI / API Client / Mobile App                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    API 网关层                             │
│  Nginx + HTTPS + 限流 + 认证                             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Web 服务层                              │
│  FastAPI + Uvicorn (ASGI)                               │
│  - 认证中间件 (JWT)                                      │
│  - 日志中间件                                            │
│  - 跨域中间件 (CORS)                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  业务逻辑层                              │
│  - NL2SQL 引擎                                           │
│  - RAG 引擎                                              │
│  - 融合引擎                                              │
│  - 缓存层 (Redis)                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    数据层                                │
│  MySQL (结构化) + ChromaDB (向量) + MinIO (文档)        │
└─────────────────────────────────────────────────────────┘
```

---

### 1.2 Web 框架选型

| 框架 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| **性能** | ⭐⭐⭐⭐⭐ (ASGI) | ⭐⭐⭐ (WSGI) | ⭐⭐⭐ (WSGI) |
| **异步支持** | ✅ 原生 | ⚠️ 有限 | ⚠️ 有限 |
| **自动文档** | ✅ Swagger/ReDoc | ❌ 需插件 | ❌ 需插件 |
| **类型检查** | ✅ Pydantic | ❌ 无 | ⚠️ 有限 |
| **学习曲线** | 低 | 低 | 中 |
| **社区** | 活跃 | 非常活跃 | 非常活跃 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**✅ 推荐：FastAPI**

**理由：**
1. **高性能** - ASGI 异步支持，性能接近 Node.js
2. **自动文档** - 内置 Swagger UI 和 ReDoc
3. **类型安全** - Pydantic 数据验证
4. **易上手** - 学习曲线低，代码简洁
5. **生态好** - 与 NL2SQL/RAG 模块完美集成

---

### 1.3 API 设计

**API 风格：** RESTful

**设计原则：**
- 资源导向（/queries, /documents, /users）
- 使用 HTTP 方法（GET/POST/PUT/DELETE）
- 统一响应格式
- 版本控制（/api/v1/）

**响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": {...},
  "timestamp": "2026-04-13T19:00:00Z"
}
```

**错误格式：**
```json
{
  "code": 400,
  "message": "Invalid query parameter",
  "details": {...},
  "timestamp": "2026-04-13T19:00:00Z"
}
```

---

### 1.4 认证机制

**认证方式：** JWT (JSON Web Token)

**流程：**
```
1. 用户登录 → 2. 验证凭据 → 3. 生成 JWT → 4. 返回 Token
5. 客户端存储 Token → 6. 请求时携带 Token → 7. 服务端验证
```

**Token 结构：**
```python
{
  "user_id": "user123",
  "username": "zhangsan",
  "role": "analyst",
  "exp": 1713024000,  # 过期时间
  "iat": 1712937600   # 签发时间
}
```

**安全措施：**
- Token 有效期：24 小时
- Refresh Token：7 天
- HTTPS 传输
- 密码 bcrypt 加密

---

### 1.5 部署方式

**推荐：Docker 容器化部署**

**Dockerfile 示例：**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose：**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/caiwu
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
  
  redis:
    image: redis:7.0
```

---

## 📋 API 接口设计

### 2.1 核心接口

#### POST /api/v1/query - 自然语言查询

**请求：**
```json
{
  "query": "贵州茅台 2024 年的营业收入是多少？",
  "intent": "auto",
  "n_results": 5
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "贵州茅台 2024 年的营业收入为 1234.56 亿元。",
    "sql_result": {...},
    "document_context": [...],
    "confidence": 0.95,
    "attribution": {...}
  },
  "timestamp": "2026-04-13T19:00:00Z"
}
```

---

#### GET /api/v1/health - 健康检查

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "services": {
      "database": "up",
      "redis": "up",
      "chromadb": "up"
    }
  },
  "timestamp": "2026-04-13T19:00:00Z"
}
```

---

#### GET /api/v1/docs - API 文档

**说明：** Swagger UI 自动文档

**访问：** http://localhost:8000/api/v1/docs

---

#### POST /api/v1/chat - 多轮对话（可选）

**请求：**
```json
{
  "query": "那净利润呢？",
  "session_id": "session123",
  "history": [...]
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "贵州茅台 2024 年的净利润为 623.45 亿元。",
    "session_id": "session123",
    "history": [...]
  },
  "timestamp": "2026-04-13T19:00:00Z"
}
```

---

### 2.2 辅助接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/refresh` | POST | 刷新 Token |
| `/api/v1/companies` | GET | 公司列表 |
| `/api/v1/companies/{code}` | GET | 公司详情 |
| `/api/v1/documents` | GET | 文档列表 |
| `/api/v1/cache/stats` | GET | 缓存统计 |

---

## 📊 技术栈汇总

| 层级 | 技术 | 版本 |
|------|------|------|
| **Web 框架** | FastAPI | 0.100+ |
| **ASGI 服务器** | Uvicorn | 0.23+ |
| **数据验证** | Pydantic | 2.0+ |
| **认证** | PyJWT | 2.8+ |
| **密码加密** | bcrypt | 4.0+ |
| **缓存** | Redis | 7.0+ |
| **数据库** | MySQL | 8.0+ |
| **向量库** | ChromaDB | 0.4+ |
| **部署** | Docker | 24.0+ |

---

**中书省 谨拟**  
天启二年四月十三日（2026 年 4 月 13 日）19:15
