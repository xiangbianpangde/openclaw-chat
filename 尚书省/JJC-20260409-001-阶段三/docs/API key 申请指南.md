# Qwen API Key 申请指南

**版本：** v1.0  
**日期：** 天启二年四月十三日（2026 年 4 月 13 日）  
**用途：** 阶段三 NL2SQL 引擎真实 LLM 测试

---

## 📋 申请步骤

### 步骤 1：注册阿里云账号

**网址：** https://www.aliyun.com/

**所需信息：**
- 手机号
- 邮箱
- 身份证（实名认证）

**时间：** 约 5 分钟

### 步骤 2：开通 DashScope 服务

**网址：** https://dashscope.console.aliyun.com/

**步骤：**
1. 登录阿里云控制台
2. 搜索"DashScope"
3. 点击"开通服务"
4. 同意服务协议

**时间：** 约 3 分钟

### 步骤 3：获取 API Key

**步骤：**
1. 进入 DashScope 控制台
2. 点击"API Key 管理"
3. 点击"创建 API Key"
4. 复制 API Key（格式：`sk-xxxxxxxxxxxxxxxx`）

**时间：** 约 2 分钟

### 步骤 4：充值（新用户免费¥200）

**步骤：**
1. 进入"费用中心"
2. 新用户自动获得¥200 免费额度
3. 无需额外充值

**有效期：** 免费额度 30 天有效

---

## 💰 成本预估

### Qwen API 价格（2026 年）

| 模型 | 输入价格 | 输出价格 | 推荐度 |
|------|---------|---------|--------|
| qwen-turbo | ¥0.002/1K tokens | ¥0.006/1K tokens | ⭐⭐⭐⭐ |
| **qwen-plus** | **¥0.004/1K tokens** | **¥0.012/1K tokens** | **⭐⭐⭐⭐⭐** |
| qwen-max | ¥0.04/1K tokens | ¥0.12/1K tokens | ⭐⭐⭐ |

### 20 条测试查询成本预估

**假设：**
- 每条 Prompt 约 2000 tokens（输入）
- 每条 SQL 约 100 tokens（输出）
- 共 20 条测试

**计算：**
```
输入成本：20 × 2000 tokens × ¥0.004/1K = ¥0.16
输出成本：20 × 100 tokens × ¥0.012/1K = ¥0.024
总计：¥0.184
```

**结论：** 20 条测试成本约**¥0.20**（远低于免费¥200 额度）

### 全阶段三成本预估

**假设：**
- Day 2-4：每日 20 条测试
- 共 3 日：60 条测试
- 后续优化：100 条测试

**总成本：** 约**¥1.00**（仍在免费额度内）

---

## 🔧 配置方法

### 环境变量配置

```bash
# Linux/Mac
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxx"

# Windows
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### Python 代码配置

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxxxxxxxxxxxxxx",  # 替换为真实 API key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "你好"}]
)

print(response.choices[0].message.content)
```

### 配置文件配置

**文件：** `config/api_key.env`

```ini
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx
QWEN_MODEL=qwen-plus
```

---

## ⚠️ 注意事项

### 1. API Key 安全

- ❌ **不要**将 API Key 提交到代码仓库
- ✅ **使用**环境变量或配置文件
- ✅ **定期**轮换 API Key

### 2. 免费额度限制

- 新用户免费¥200 额度
- 有效期 30 天
- 超出后按量计费

### 3. 调用限制

| 限制类型 | 默认值 | 可申请提升 |
|---------|--------|-----------|
| QPS（每秒查询数） | 10 | 是 |
| 日调用次数 | 10000 | 是 |
| 月调用金额 | ¥200（免费额度） | 充值后提升 |

---

## 📞 技术支持

**阿里云 DashScope 支持：**
- 官网：https://help.aliyun.com/product/dashscope.html
- 客服：95187
- 工单：控制台提交

---

## 📅 申请时间线

| 步骤 | 预计时间 | 实际完成 |
|------|---------|---------|
| 注册阿里云账号 | 5 分钟 | ⏳ |
| 开通 DashScope 服务 | 3 分钟 | ⏳ |
| 获取 API Key | 2 分钟 | ⏳ |
| 配置 API Key | 5 分钟 | ⏳ |
| **总计** | **15 分钟** | ⏳ |

---

**尚书省 谨记**  
天启二年四月十三日（2026 年 4 月 13 日）11:45  
**API Key 申请指南已准备，15 分钟可完成！** 📋
