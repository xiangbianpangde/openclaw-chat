# OpenClaw Chat 部署指南

## 快速部署（5 分钟）

### 1. 准备服务器

**最低配置：**
- CPU: 2 核
- 内存：4GB
- 存储：20GB
- 系统：Ubuntu 20.04+ / Debian 11+

**开放端口：**
```bash
sudo ufw allow 10001:10010/tcp  # OpenIM
sudo ufw allow 11001/tcp        # Web 管理
sudo ufw allow 6080/tcp         # noVNC
sudo ufw allow 7891/tcp         # Edict 看板
```

### 2. 安装依赖

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 3. 克隆项目

```bash
cd /opt
git clone https://github.com/xiangbianpangde/openclaw-chat.git
cd openclaw-chat
```

### 4. 配置服务器 IP

```bash
# 获取公网 IP（自动）
export OPENIM_IP=$(curl -s ifconfig.me)

# 或手动指定
export OPENIM_IP="你的服务器 IP"

echo "服务器 IP: $OPENIM_IP"
```

### 5. 启动服务

```bash
cd server

# 运行初始化脚本
./scripts/init.sh

# 或手动启动
docker compose up -d
```

### 6. 验证部署

```bash
# 检查所有服务
docker compose ps

# 应该看到：
# openclaw-mongo     Running
# openclaw-redis     Running
# openclaw-minio     Running
# openclaw-server    Running
# openclaw-chat      Running
# openclaw-novnc     Running
# openclaw-vnc       Running
# openclaw-web       Running
```

### 7. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| OpenIM Web | `http://IP:11001` | 用户管理后台 |
| noVNC | `http://IP:6080` | 远程桌面 |
| MinIO | `http://IP:9001` | 文件存储管理 |
| Edict 看板 | `http://IP:7891` | OpenClaw 监控 |

---

## 创建用户账号

### 方法 1：Web 管理后台

1. 访问 `http://IP:11001`
2. 登录：
   - 用户：`admin`
   - 密码：`openIM123`
3. 用户管理 → 创建用户
4. 填写信息：
   - 用户 ID: `user001`
   - 昵称：`测试用户`
   - 密码：`123456`

### 方法 2：命令行

```bash
curl -X POST "http://$OPENIM_IP:10002/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userID": "user001",
    "nickname": "测试用户",
    "secret": "123456"
  }'
```

---

## 客户端部署

### Android APK 编译

```bash
# 安装 Flutter
sudo snap install flutter --classic

# 配置 Flutter
flutter doctor

# 克隆项目
git clone https://github.com/xiangbianpangde/openclaw-chat.git
cd openclaw-chat/client/openclaw_chat

# 安装依赖
flutter pub get

# 编译 APK
flutter build apk --release

# APK 位置
ls -lh build/app/outputs/flutter-apk/app-release.apk
```

### iOS 编译

```bash
cd client/openclaw_chat
flutter build ios --release
```

使用 Xcode 签名后发布到 TestFlight。

### Web 版

```bash
cd client/openclaw_chat
flutter build web
flutter run -d web-server --web-port=8080 --web-hostname=0.0.0.0
```

访问：`http://服务器 IP:8080`

---

## OpenClaw 集成

### 1. 配置 OpenClaw

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "extensions": {
    "openim": {
      "enabled": true,
      "serverUrl": "http://localhost:10002",
      "botUserId": "openclaw_bot",
      "adminToken": "YOUR_ADMIN_TOKEN"
    }
  }
}
```

### 2. 创建机器人账号

```bash
curl -X POST "http://$OPENIM_IP:10002/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userID": "openclaw_bot",
    "nickname": "OpenClaw 助手",
    "ex": "OpenClaw 官方机器人"
  }'
```

### 3. 启动扩展服务

```bash
cd server/openclaw-extension
npm install
npm start
```

### 4. 测试

在 App 中与 `OpenClaw 助手` 对话：

```
/help
```

---

## 常见问题

### Q: 服务启动失败？

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 清理重建
docker compose down
docker compose up -d
```

### Q: 无法访问 Web 界面？

```bash
# 检查防火墙
sudo ufw status

# 开放端口
sudo ufw allow 11001/tcp

# 检查服务
docker compose ps
```

### Q: 消息发送失败？

```bash
# 检查 OpenIM 服务
docker logs openclaw-server

# 检查 Bot 账号
curl "http://$OPENIM_IP:10002/user/get_users_public" \
  -d '{"userIDList":["openclaw_bot"]}'
```

### Q: 如何备份数据？

```bash
# 备份 MongoDB
docker exec openclaw-mongo mongodump --out /backup

# 备份 MinIO
mc cp -r openim/minio-data /backup/minio

# 备份配置文件
tar -czf openclaw-config-backup.tar.gz \
  server/data/openim/config \
  .env
```

---

## 性能优化

### 内存限制

编辑 `docker-compose.yml`，调整内存限制：

```yaml
services:
  mongo:
    deploy:
      resources:
        limits:
          memory: 400M  # 根据服务器调整
```

### 日志轮转

```bash
# 创建日志配置
cat > /etc/docker/daemon.json << 'DOCKEREOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
DOCKEREOF

# 重启 Docker
sudo systemctl restart docker
```

---

## 安全加固

### 修改默认密码

```bash
# 修改 MongoDB 密码
docker exec openclaw-mongo mongosh \
  -u openim -p openim123 \
  --eval "db.user.updateOne({userID:'admin'}, {\$set:{password:'NEW_PASSWORD'}})"

# 修改 Redis 密码
# 编辑 docker-compose.yml 中的 REDIS_PASSWORD
```

### 启用 HTTPS

```bash
# 使用 Nginx 反向代理
sudo apt install nginx

# 配置 SSL
sudo certbot --nginx -d your-domain.com
```

### 限制访问 IP

```bash
# 只允许特定 IP 访问
sudo ufw allow from 192.168.1.0/24 to any port 10001:10010
```

---

## 监控与告警

### Prometheus + Grafana

```yaml
# 添加到 docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 日志聚合

```bash
# 使用 Loki + Promtail
docker run -d --name loki grafana/loki:latest
docker run -d --name promtail grafana/promtail:latest
```

---

## 升级指南

```bash
# 拉取最新代码
cd /opt/openclaw-chat
git pull

# 停止服务
docker compose down

# 更新镜像
docker compose pull

# 重启服务
docker compose up -d

# 清理旧镜像
docker image prune -f
```

---

## 技术支持

- **GitHub Issues**: https://github.com/xiangbianpangde/openclaw-chat/issues
- **文档**: https://github.com/xiangbianpangde/openclaw-chat/docs
- **社区**: 加入 OpenClaw Discord 社区
