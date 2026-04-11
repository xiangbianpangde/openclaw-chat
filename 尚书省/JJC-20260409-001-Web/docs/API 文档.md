# API 文档

**产品名称：** 财报智能问数助手 API  
**版本：** v1.0  
**日期：** 天启二年四月十三日（2026 年 4 月 13 日）

---

## 📖 API 概述

- **Base URL:** `http://localhost:8000/api/v1`
- **认证方式:** Bearer Token
- **数据格式:** JSON

---

## 🔑 认证

### 用户登录

**请求：**
```http
POST /api/v1/auth/login
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

---

## 📋 API 端点

### 1. 自然语言查询

**端点：** `POST /api/v1/query`

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
  "answer": "贵州茅台 2024 年的营业收入为 1234.56 亿元。",
  "confidence": 0.95,
  "attribution": {...}
}
```

---

### 2. 健康检查

**端点：** `GET /api/v1/health`

**响应：**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 3. 版本信息

**端点：** `GET /api/v1/version`

**响应：**
```json
{
  "version": "1.0.0",
  "api_version": "v1",
  "build_date": "2026-04-13"
}
```

---

**尚书省 谨记**  
天启二年四月十三日（2026 年 4 月 13 日）
