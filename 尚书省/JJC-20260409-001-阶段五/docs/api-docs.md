# API 文档

**产品名称：** 财报智能问数助手 API  
**版本：** v1.0  
**日期：** 天启二年四月十三日（2026 年 4 月 13 日）

---

## 📖 API 概述

### 基础信息

- **Base URL:** `https://api.caiwu-assistant.com/v1`
- **认证方式:** Bearer Token
- **数据格式:** JSON

---

## 🔑 认证

### 获取 Token

**请求：**
```http
POST /auth/token
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 使用 Token

```http
GET /query
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📋 API 端点

### 1. 查询接口

**端点：** `POST /query`

**请求：**
```json
{
  "query": "贵州茅台 2024 年的营业收入是多少？",
  "intent": "auto",
  "n_results": 5
}
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 查询文本 |
| intent | string | ❌ | 查询意图（auto/fact/analysis/explanation） |
| n_results | integer | ❌ | 返回结果数量（默认 5） |

**响应：**
```json
{
  "answer": "贵州茅台 2024 年的营业收入为 1234.56 亿元。",
  "sql_result": {
    "revenue": 123456000000,
    "period": "2024"
  },
  "document_context": [
    "贵州茅台 2024 年年度报告显示..."
  ],
  "confidence": 0.95,
  "attribution": {
    "type": "hybrid",
    "sql": "SELECT revenue FROM...",
    "docs": 1
  }
}
```

---

### 2. 健康检查

**端点：** `GET /health`

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-13T18:00:00Z",
  "version": "1.0.0"
}
```

---

### 3. 批量查询

**端点：** `POST /query/batch`

**请求：**
```json
{
  "queries": [
    "贵州茅台 2024 年的营收是多少？",
    "五粮液 2023 年的净利润是多少？"
  ]
}
```

**响应：**
```json
{
  "results": [
    {
      "query": "贵州茅台 2024 年的营收是多少？",
      "answer": "1234.56 亿元",
      "confidence": 0.95
    },
    {
      "query": "五粮液 2023 年的净利润是多少？",
      "answer": "987.65 亿元",
      "confidence": 0.93
    }
  ]
}
```

---

## ❌ 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 📊 限流

| 套餐 | QPS | 日限额 |
|------|-----|--------|
| 免费 | 1 | 100 |
| 基础 | 10 | 10000 |
| 专业 | 100 | 100000 |
| 企业 | 1000 | 不限 |

---

## 📞 技术支持

**联系方式：**
- 邮箱：api-support@caiwu-assistant.com
- 文档：https://docs.caiwu-assistant.com

---

**尚书省 谨记**  
天启二年四月十三日（2026 年 4 月 13 日）18:00  
**API 文档完成！** 📋
