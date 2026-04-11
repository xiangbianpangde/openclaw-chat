# 部署指南

**产品名称：** 财报智能问数助手  
**版本：** v1.0  
**日期：** 天启二年四月十三日（2026 年 4 月 13 日）

---

## 📖 部署概述

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户层                               │
│  Web UI / API / CLI                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    API 网关层                             │
│  FastAPI + Nginx                                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  应用服务层                              │
│  NL2SQL 引擎 + RAG 引擎 + 融合引擎                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    数据层                                │
│  MySQL + ChromaDB + Redis                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速部署

### 1. 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 必需 |
| MySQL | 8.0+ | 结构化数据存储 |
| ChromaDB | 0.4+ | 向量数据库 |
| Redis | 7.0+ | 缓存 |

### 2. 安装依赖

```bash
# 克隆代码
git clone https://github.com/caiwu-assistant/core.git
cd core

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# .env 文件
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/caiwu
REDIS_URL=redis://localhost:6379/0
CHROMA_DB_PATH=./chroma_db
API_KEY=your_api_key
```

### 4. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE caiwu CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移
python scripts/migrate.py
```

### 5. 启动服务

```bash
# 开发模式
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 🐳 Docker 部署

### 1. 构建镜像

```bash
docker build -t caiwu-assistant:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name caiwu-assistant \
  -p 8000:8000 \
  -v ./data:/app/data \
  -e DATABASE_URL=mysql+pymysql://user:password@mysql:3306/caiwu \
  -e REDIS_URL=redis://redis:6379/0 \
  caiwu-assistant:latest
```

### 3. Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:password@mysql:3306/caiwu
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: caiwu
  
  redis:
    image: redis:7.0
```

---

## ⚙️ 生产配置

### 1. Nginx 配置

```nginx
server {
    listen 80;
    server_name api.caiwu-assistant.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. HTTPS 配置

```bash
# 使用 Let's Encrypt
certbot --nginx -d api.caiwu-assistant.com
```

### 3. 监控配置

```yaml
# Prometheus 配置
scrape_configs:
  - job_name: 'caiwu-assistant'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## 🔧 运维

### 1. 日志查看

```bash
# 应用日志
tail -f logs/app.log

# Nginx 日志
tail -f /var/log/nginx/access.log
```

### 2. 性能监控

```bash
# 查看 QPS
watch -n 1 'curl -s http://localhost:8000/health'

# 查看内存
ps aux | grep python
```

### 3. 备份恢复

```bash
# 备份数据库
mysqldump -u root -p caiwu > backup.sql

# 恢复数据库
mysql -u root -p caiwu < backup.sql
```

---

## ❓ 故障排查

### 问题 1：服务无法启动

**检查：**
```bash
# 查看日志
tail -f logs/app.log

# 检查端口
netstat -tlnp | grep 8000
```

### 问题 2：查询响应慢

**检查：**
```bash
# 查看慢查询
mysql -u root -p -e "SHOW PROCESSLIST;"

# 查看缓存命中率
redis-cli INFO stats
```

### 问题 3：内存占用高

**检查：**
```bash
# 查看进程内存
ps aux --sort=-%mem | head

# 重启服务
systemctl restart caiwu-assistant
```

---

## 📞 技术支持

**联系方式：**
- 邮箱：ops@caiwu-assistant.com
- 电话：400-806-1866

---

**尚书省 谨记**  
天启二年四月十三日（2026 年 4 月 13 日）18:00  
**部署指南完成！** 📋
