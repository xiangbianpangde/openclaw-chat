# API 接口设计文档

**版本：** v1.0  
**日期：** 2026 年 4 月 9 日

---

## 一、接口概览

| 模块 | 前缀 | 说明 |
|------|------|------|
| 健康检查 | `/api/health` | 服务健康状态 |
| 认证授权 | `/api/auth` | 用户登录、Token 管理 |
| PDF 管理 | `/api/pdf` | PDF 上传、解析、状态查询 |
| 数据查询 | `/api/query` | NL2SQL 查询、SQL 执行、财务数据 |
| 系统管理 | `/api/admin` | 审计日志、统计、任务管理 |

---

## 二、健康检查接口

### 2.1 基础健康检查

```http
GET /api/health/
```

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-09T15:00:00",
  "version": "0.1.0"
}
```

### 2.2 详细健康检查

```http
GET /api/health/detailed
```

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-09T15:00:00",
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "memory_available_mb": 17408,
    "disk_percent": 60.1,
    "disk_free_gb": 200.5
  },
  "services": {
    "api": "up",
    "database": "up",
    "redis": "up",
    "minio": "up"
  }
}
```

---

## 三、认证授权接口

### 3.1 用户登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 3.2 获取当前用户信息

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**响应：**
```json
{
  "user_id": "admin",
  "username": "admin",
  "role": "admin",
  "is_active": true
}
```

---

## 四、PDF 管理接口

### 4.1 上传单个 PDF

```http
POST /api/pdf/upload
Content-Type: multipart/form-data

file: <PDF 文件>
company_code: 600519
report_year: 2023
report_type: 年报
```

**响应：**
```json
{
  "message": "上传成功",
  "file_path": "./data/raw/600519/2023.pdf",
  "file_size": 10485760,
  "file_hash": "abc123...",
  "company_code": "600519",
  "report_year": 2023
}
```

### 4.2 批量上传 PDF

```http
POST /api/pdf/batch-upload
Content-Type: multipart/form-data

files: <多个 PDF 文件>
```

**响应：**
```json
{
  "total": 10,
  "success": 8,
  "failed": 2,
  "results": [
    {
      "filename": "600519_2023.pdf",
      "status": "success",
      "file_path": "./data/raw/batch/600519_2023.pdf",
      "file_size": 10485760,
      "file_hash": "abc123..."
    },
    {
      "filename": "invalid.pdf",
      "status": "failed",
      "error": "文件大小超过限制"
    }
  ]
}
```

### 4.3 查询解析任务状态

```http
GET /api/pdf/parse-status/{task_id}
```

**响应：**
```json
{
  "task_id": "task_20260409_001",
  "status": "running",
  "total_files": 100,
  "completed_files": 45,
  "failed_files": 2,
  "progress": 0.45
}
```

---

## 五、数据查询接口

### 5.1 自然语言查询（NL2SQL）

```http
POST /api/query/natural-language
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "贵州茅台 2023 年的营业收入是多少？",
  "company_code": "600519",
  "report_year": 2023,
  "top_k": 5
}
```

**响应：**
```json
{
  "query": "贵州茅台 2023 年的营业收入是多少？",
  "sql": "SELECT metric_value FROM financial_data WHERE company_code = '600519' AND report_year = 2023 AND metric_name = '营业收入'",
  "data": [
    {
      "company_code": "600519",
      "report_year": 2023,
      "metric_name": "营业收入",
      "metric_value": 123456789.00,
      "unit": "元"
    }
  ],
  "total": 1,
  "execution_time_ms": 125.5,
  "source": "nl2sql"
}
```

### 5.2 获取公司财务数据

```http
GET /api/query/financial/{company_code}?year=2023
Authorization: Bearer <token>
```

**响应：**
```json
{
  "company_code": "600519",
  "year": 2023,
  "metrics": [
    {"name": "营业收入", "value": 123456.78, "unit": "万元", "year": 2023},
    {"name": "净利润", "value": 23456.78, "unit": "万元", "year": 2023},
    {"name": "总资产", "value": 345678.90, "unit": "万元", "year": 2023}
  ]
}
```

### 5.3 多公司比较

```http
GET /api/query/compare?companies=600519,000858,000568&metric=毛利率&year=2023
Authorization: Bearer <token>
```

**响应：**
```json
{
  "metric": "毛利率",
  "year": 2023,
  "comparison": [
    {"company_code": "600519", "value": 0.92, "rank": 1},
    {"company_code": "000858", "value": 0.75, "rank": 2},
    {"company_code": "000568", "value": 0.70, "rank": 3}
  ]
}
```

---

## 六、系统管理接口

### 6.1 查询审计日志

```http
GET /api/admin/audit-logs?user_id=admin&limit=100
Authorization: Bearer <token>
```

**响应：**
```json
{
  "logs": [
    {
      "id": 1,
      "user_id": "admin",
      "action": "query",
      "resource": "/api/query/natural-language",
      "method": "POST",
      "response_status": 200,
      "response_time_ms": 125.5,
      "ip_address": "192.168.1.100",
      "created_at": "2026-04-09T15:00:00"
    }
  ],
  "total": 1
}
```

### 6.2 系统统计

```http
GET /api/admin/stats
Authorization: Bearer <token>
```

**响应：**
```json
{
  "total_companies": 500,
  "total_pdfs": 2500,
  "total_parse_tasks": 50,
  "total_queries_today": 120,
  "avg_query_time_ms": 150.5
}
```

### 6.3 列出解析任务

```http
GET /api/admin/tasks?status=running
Authorization: Bearer <token>
```

**响应：**
```json
{
  "tasks": [
    {
      "task_id": "task_20260409_001",
      "status": "running",
      "total_files": 100,
      "completed_files": 45,
      "created_at": "2026-04-09T14:00:00"
    }
  ]
}
```

---

## 七、错误响应格式

```json
{
  "detail": "错误描述信息",
  "error": "具体错误类型（仅调试模式）"
}
```

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权（Token 无效/过期） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |

---

## 八、速率限制

| 角色 | 限流策略 |
|------|---------|
| admin | 1000 次/分钟 |
| analyst | 100 次/分钟 |
| viewer | 50 次/分钟 |
| uploader | 10 次/分钟 |

---

**尚书省 制定**  
天启二年四月初九（2026 年 4 月 9 日）
