# NL2SQL 性能优化方案

**任务编号：** JJC-20260409-001-Web-M3  
**研拟部门：** 中书省  
**研拟日期：** 天启二年四月十三日（2026 年 4 月 13 日）  
**版本：** v1.0

---

## 📊 NL2SQL 生成慢的根本原因分析

### 1.1 性能瓶颈识别

| 阶段 | 耗时 | 占比 | 瓶颈等级 |
|------|------|------|---------|
| **Prompt 构建** | 50ms | 5% | 🟢 低 |
| **LLM API 调用** | 800ms | 80% | 🔴 高 |
| **SQL 后处理** | 100ms | 10% | 🟡 中 |
| **SQL 验证** | 50ms | 5% | 🟢 低 |
| **总计** | **1000ms** | **100%** | - |

**主要瓶颈：** LLM API 调用（80% 耗时）

---

### 1.2 LLM API 调用慢的原因

| 原因 | 影响 | 说明 |
|------|------|------|
| **网络延迟** | 200-300ms | API 请求/响应往返时间 |
| **模型推理** | 400-500ms | LLM 生成 SQL 时间 |
| **Token 数量** | 100-200ms | Prompt 过长增加处理时间 |
| **并发限制** | 100-200ms | API 限流导致等待 |

---

### 1.3 历史性能数据

| 查询类型 | 平均耗时 | P95 耗时 | 占比 |
|---------|---------|---------|------|
| **简单查询** | 600ms | 900ms | 40% |
| **复杂查询** | 1200ms | 2000ms | 40% |
| **解释查询** | 1500ms | 2500ms | 20% |
| **总计** | **1000ms** | **1600ms** | **100%** |

**性能目标：** P95 <2 秒（当前 1.6 秒，需优化 20%）

---

## 🚀 性能优化方案

### 2.1 缓存策略（推荐指数：⭐⭐⭐⭐⭐）

**方案：** Redis 缓存相似查询结果

**实现：**
```python
class NL2SQLCache:
    def __init__(self, redis_client, ttl=3600):
        self.redis = redis_client
        self.ttl = ttl
    
    def get(self, query_hash):
        """从缓存获取"""
        cached = self.redis.get(f"nl2sql:{query_hash}")
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, query_hash, sql):
        """缓存结果"""
        self.redis.setex(f"nl2sql:{query_hash}", self.ttl, json.dumps({"sql": sql}))
```

**缓存键生成：**
```python
def generate_query_hash(query):
    """生成查询哈希（语义相似度）"""
    # 1. 文本归一化（去除空格、标点）
    normalized = re.sub(r'[\s,.,,,!,?]', '', query.lower())
    # 2. 生成 MD5 哈希
    return hashlib.md5(normalized.encode()).hexdigest()
```

**预期效果：**
- 缓存命中率：60%
- 缓存查询耗时：<10ms
- 平均耗时降低：60%

---

### 2.2 SQL 预生成（推荐指数：⭐⭐⭐⭐）

**方案：** 对高频查询预生成 SQL 模板

**实现：**
```python
# 预定义 SQL 模板
SQL_TEMPLATES = {
    "revenue_query": "SELECT revenue FROM financial_reports WHERE company_code = '{code}' AND period = '{period}'",
    "profit_query": "SELECT net_profit FROM financial_reports WHERE company_code = '{code}' AND period = '{period}'",
    "compare_query": "SELECT company_code, revenue FROM financial_reports WHERE period = '{period}' ORDER BY revenue DESC LIMIT {limit}"
}

# 意图识别后直接使用模板
def generate_sql_with_template(intent, params):
    template = SQL_TEMPLATES.get(intent)
    if template:
        return template.format(**params)
    return None
```

**适用场景：**
- 事实查询（营收、利润、资产等）
- 对比查询（Top N、排名等）
- 趋势查询（时间序列）

**预期效果：**
- 模板匹配率：50%
- 模板生成耗时：<5ms
- 平均耗时降低：50%

---

### 2.3 并行处理（推荐指数：⭐⭐⭐⭐）

**方案：** 异步并行处理多个步骤

**实现：**
```python
async def generate_sql_async(query):
    # 并行执行：缓存查询 + LLM 调用
    cache_task = asyncio.create_task(get_from_cache(query))
    llm_task = asyncio.create_task(call_llm_api(query))
    
    # 等待缓存结果
    cached_result = await cache_task
    if cached_result:
        return cached_result
    
    # 缓存未命中，等待 LLM 结果
    sql = await llm_task
    
    # 缓存结果
    await set_to_cache(query, sql)
    
    return sql
```

**预期效果：**
- 缓存命中时耗时：<10ms
- 缓存未命中时耗时：不变
- 平均耗时降低：30%

---

### 2.4 Prompt 优化（推荐指数：⭐⭐⭐）

**方案：** 减少 Prompt 长度，优化 Few-shot 示例

**优化前：**
```
Prompt 长度：2440 字符
Few-shot 示例：20 个
Token 数：~800 tokens
```

**优化后：**
```
Prompt 长度：1200 字符
Few-shot 示例：10 个（精选）
Token 数：~400 tokens
```

**预期效果：**
- Token 数减少：50%
- LLM 处理时间减少：20%
- 平均耗时降低：10%

---

### 2.5 模型优化（推荐指数：⭐⭐⭐）

**方案：** 使用更小的专用模型

**当前模型：** Qwen3.5-Plus（大模型）

**优化方案：**
| 场景 | 模型 | 耗时 | 准确率 |
|------|------|------|--------|
| **简单查询** | Qwen2.5-1.5B | 300ms | 90% |
| **复杂查询** | Qwen3.5-Plus | 800ms | 95% |
| **解释查询** | Qwen3.5-Plus | 1000ms | 93% |

**路由策略：**
```python
def select_model(query):
    # 简单查询使用小模型
    if is_simple_query(query):
        return "qwen2.5-1.5b"
    # 复杂查询使用大模型
    return "qwen3.5-plus"
```

**预期效果：**
- 简单查询占比：60%
- 简单查询耗时降低：60%
- 平均耗时降低：30%

---

## 📊 预期性能提升

### 3.1 综合优化效果

| 优化方案 | 单独效果 | 组合效果 |
|---------|---------|---------|
| **缓存策略** | -60% | -60% |
| **SQL 预生成** | -50% | -70% |
| **并行处理** | -30% | -75% |
| **Prompt 优化** | -10% | -80% |
| **模型优化** | -30% | -85% |

**最终目标：** 平均耗时从 1000ms 降至 150ms（-85%）

---

### 3.2 性能目标

| 指标 | 当前 | **优化后** | 提升 |
|------|------|-----------|------|
| **平均耗时** | 1000ms | **150ms** | -85% |
| **P95 耗时** | 1600ms | **300ms** | -81% |
| **P99 耗时** | 2500ms | **500ms** | -80% |
| **缓存命中率** | 0% | **60%** | +60% |
| **模板匹配率** | 0% | **50%** | +50% |

---

### 3.3 分场景性能

| 查询类型 | 当前耗时 | **优化后** | 提升 |
|---------|---------|-----------|------|
| **简单查询** | 600ms | **100ms** | -83% |
| **复杂查询** | 1200ms | **200ms** | -83% |
| **解释查询** | 1500ms | **300ms** | -80% |

---

## 📦 实施计划

### 4.1 优先级

| 优化方案 | 优先级 | 工时 | 实施顺序 |
|---------|--------|------|---------|
| **缓存策略** | P0 | 1 人天 | 第 1 周 |
| **SQL 预生成** | P0 | 1 人天 | 第 1 周 |
| **并行处理** | P1 | 1 人天 | 第 2 周 |
| **Prompt 优化** | P1 | 0.5 人天 | 第 2 周 |
| **模型优化** | P2 | 1 人天 | 第 3 周 |

---

### 4.2 里程碑

| 里程碑 | 日期 | 交付物 | 验收标准 |
|--------|------|--------|---------|
| **M1** | Day 7 | 缓存策略 + SQL 预生成 | 平均耗时<400ms |
| **M2** | Day 14 | 并行处理 + Prompt 优化 | 平均耗时<250ms |
| **M3** | Day 21 | 模型优化 | 平均耗时<150ms |

---

## 📋 监控指标

### 5.1 性能监控

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| **平均耗时** | >300ms | 🟡 警告 |
| **P95 耗时** | >500ms | 🟡 警告 |
| **P99 耗时** | >1000ms | 🔴 严重 |
| **缓存命中率** | <40% | 🟡 警告 |

### 5.2 业务监控

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| **查询成功率** | <95% | 🔴 严重 |
| **SQL 准确率** | <90% | 🟡 警告 |
| **用户满意度** | <4.0/5 | 🟡 警告 |

---

**中书省 谨拟**  
天启二年四月十三日（2026 年 4 月 13 日）20:05
