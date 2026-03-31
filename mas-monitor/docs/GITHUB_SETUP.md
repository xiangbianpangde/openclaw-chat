# GitHub 设置指南

## 1. 创建 MAS-Analysis 仓库

### 方法 A: 使用 GitHub CLI
```bash
# 登录 GitHub
gh auth login

# 创建公开仓库
gh repo create xiangbianpangde/MAS-Analysis \
  --public \
  --description "MAS 库独立分析报告" \
  --source=. \
  --remote=origin
```

### 方法 B: 网页创建
1. 访问 https://github.com/new
2. 仓库名：`MAS-Analysis`
3. 描述：`MAS 库独立分析报告`
4. 可见性：**公开 (Public)**
5. 点击 "Create repository"

## 2. 配置 GitHub Token

### 创建 Personal Access Token
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 备注：`MAS-Monitor-Token`
4. 过期时间：建议 90 天
5. 勾选权限:
   - ✅ `repo` (完整仓库访问)
   - ✅ `read:org` (读取组织信息)
   - ✅ `workflow` (如果需要 CI/CD)
6. 点击 "Generate token"
7. **复制并保存 Token**（只显示一次）

### 配置 Token
```bash
# 临时配置（当前会话）
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 永久配置（推荐）
echo 'export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx' >> ~/.bashrc
source ~/.bashrc

# 或写入 MAS Monitor 配置
echo "GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx" > /root/.openclaw/workspace-taizi/mas-monitor/.env
```

## 3. 验证配置
```bash
# 测试 GitHub API
curl -H "Authorization: token $GH_TOKEN" \
  https://api.github.com/user

# 测试仓库访问
curl -H "Authorization: token $GH_TOKEN" \
  https://api.github.com/repos/xiangbianpangde/MAS
```

## 4. 配置 Webhook（可选）

### 在 MAS 仓库配置 Webhook
1. 访问 https://github.com/xiangbianpangde/MAS/settings/hooks
2. 点击 "Add webhook"
3. Payload URL: `<your-server>/webhook/github`
4. Content type: `application/json`
5. Secret: `<your-secret>`
6. Events: 选择 `Push`, `Pull Request`, `Release`
7. 点击 "Add webhook"

## 5. 测试 MAS Monitor
```bash
cd /root/.openclaw/workspace-taizi/mas-monitor

# 单次运行测试
npm run once

# 查看生成的报告
cat reports/realtime/summary.json
```

## 常见问题

### Q: `gh: command not found`
```bash
# 安装 GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### Q: Token 权限不足
确保 Token 包含 `repo` 权限（完整仓库访问）

### Q: 仓库不存在
确认仓库名正确：`xiangbianpangde/MAS`
