# NL2SQL 训练数据集规范

**版本：** v1.0  
**日期：** 2026 年 4 月 9 日

---

## 一、数据格式

### 1.1 训练数据 JSONL 格式

每条训练数据为一行 JSON，包含以下字段：

```json
{
  "id": "train_00001",
  "question": "贵州茅台 2023 年的营业收入是多少？",
  "sql": "SELECT metric_value FROM financial_data WHERE company_code = '600519' AND report_year = 2023 AND metric_name = '营业收入'",
  "schema": {
    "tables": ["financial_data", "companies"],
    "columns": {
      "financial_data": ["company_code", "report_year", "metric_name", "metric_value", "unit"],
      "companies": ["company_code", "company_name", "industry"]
    }
  },
  "difficulty": "easy",
  "query_type": "single_table"
}
```

### 1.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 唯一标识符 |
| question | string | ✅ | 自然语言问题 |
| sql | string | ✅ | 对应的 SQL 查询 |
| schema | object | ✅ | 数据库 schema 信息 |
| difficulty | string | ✅ | 难度等级 (easy/medium/hard) |
| query_type | string | ✅ | 查询类型 |

---

## 二、难度等级定义

### 2.1 Easy（简单）

- 单表查询
- 简单条件（=, >, <）
- 单指标查询

**示例：**
```
问题：贵州茅台 2023 年的营业收入是多少？
SQL：SELECT metric_value FROM financial_data 
     WHERE company_code = '600519' AND report_year = 2023 
     AND metric_name = '营业收入'
```

### 2.2 Medium（中等）

- 多表 JOIN
- 聚合函数（SUM, AVG, COUNT）
- 排序和 LIMIT
- 多指标查询

**示例：**
```
问题：贵州茅台最近 3 年的营业收入和净利润分别是多少？
SQL：SELECT report_year, metric_name, metric_value 
     FROM financial_data 
     WHERE company_code = '600519' 
     AND metric_name IN ('营业收入', '净利润')
     ORDER BY report_year DESC 
     LIMIT 6
```

### 2.3 Hard（困难）

- 子查询
- GROUP BY + HAVING
- 多公司比较
- 复杂计算

**示例：**
```
问题：2023 年净利润增长率超过 20% 的白酒公司有哪些？
SQL：SELECT c.company_name, 
            (fd1.metric_value - fd0.metric_value) / fd0.metric_value * 100 AS growth_rate
     FROM companies c
     JOIN financial_data fd1 ON c.company_code = fd1.company_code
     JOIN financial_data fd0 ON c.company_code = fd0.company_code
     WHERE fd1.report_year = 2023 
     AND fd0.report_year = 2022
     AND fd1.metric_name = '净利润'
     AND fd0.metric_name = '净利润'
     AND c.industry = '白酒'
     HAVING growth_rate > 20
```

---

## 三、查询类型分类

| 类型 | 说明 | 占比 |
|------|------|------|
| single_table | 单表查询 | 40% |
| multi_table | 多表 JOIN | 25% |
| aggregation | 聚合查询 | 15% |
| comparison | 比较查询 | 10% |
| trend | 趋势分析 | 5% |
| complex | 复杂查询 | 5% |

---

## 四、数据来源

### 4.1 公开数据集

| 数据集 | 数量 | 用途 |
|--------|------|------|
| Spider | 10,181 条 | 基础训练 |
| BIRD | 12,751 条 | 基础训练 |

### 4.2 合成数据

**生成策略：**

```python
# 基于模板生成
templates = [
    {
        "pattern": "{company}{year}年的{metric}是多少？",
        "sql_template": "SELECT metric_value FROM financial_data WHERE company_code = '{code}' AND report_year = {year} AND metric_name = '{metric}'"
    },
    # ... 更多模板
]
```

**目标：** 生成 50,000 条合成数据

### 4.3 人工标注

**标注流程：**

1. 收集真实用户问题（500 条）
2. 标注 SQL 查询
3. 质量审核
4. 加入训练集

---

## 五、数据质量要求

### 5.1 SQL 正确性

- ✅ 语法正确（通过 sqlparse 验证）
- ✅ 表名存在
- ✅ 列名存在
- ✅ 可执行（在测试数据库验证）

### 5.2 问题自然度

- ✅ 符合中文表达习惯
- ✅ 无语法错误
- ✅ 无歧义

### 5.3 数据分布

- ✅ 难度分布合理（easy 60%, medium 30%, hard 10%）
- ✅ 查询类型覆盖全面
- ✅ 公司代码分布均匀

---

## 六、数据集划分

| 集合 | 数量 | 用途 |
|------|------|------|
| 训练集 | 60,000 条 | 模型训练 |
| 验证集 | 10,000 条 | 超参调优 |
| 测试集 | 7,932 条 | 最终评估 |
| 人工评测集 | 500 条 | 人工质量评估 |

---

## 七、数据增强

### 7.1 同义词替换

```
营业收入 → 营收、收入、销售额
净利润 → 利润、净利、归母净利润
```

### 7.2 句式变换

```
原句：贵州茅台 2023 年的营业收入是多少？
变换 1：请查询贵州茅台 2023 年的营业收入
变换 2：2023 年贵州茅台的营业收入
变换 3：营业收入，贵州茅台，2023 年
```

---

## 八、评估指标

| 指标 | 目标值 | 计算方式 |
|------|--------|---------|
| 执行准确率 (EX) | ≥85% | SQL 执行结果与标准答案一致 |
| 精确匹配 (EM) | ≥75% | SQL 完全一致 |
| 语法正确率 | ≥95% | 语法解析验证 |
| 表名正确率 | ≥98% | 表名匹配检查 |
| 列名正确率 | ≥95% | 列名匹配检查 |

---

**尚书省 制定**  
天启二年四月初九（2026 年 4 月 9 日）
