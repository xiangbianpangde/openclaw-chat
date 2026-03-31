# OpenClaw IM 自动化测试平台

## 🚀 快速开始

### 前提条件
- 磁盘空间: 至少 8GB 可用
- 内存：至少 4GB RAM
- CPU: 至少 4 核心

### 启动开发循环

```bash
cd /root/.openclaw/workspace-taizi
./start.sh
```

## 📋 组件说明

### 目录结构
```
automation/
├── config/           # 配置文件
│   └── gateway.yaml  # Gateway 和 GitHub 配置
├── tests/            # 测试用例
│   └── test_openclaw_im.py
├── scripts/          # 自动化脚本
│   ├── dev_cycle.sh      # 主开发循环
│   └── analyze_tests.py  # 测试分析器
├── reports/          # 测试报告输出
└── logs/             # 日志文件
```

### 测试用例 (24 个)

1. **登录与认证 (1-4)**
   - App 启动
   - 登录页面显示
   - Gateway 连接
   - 认证成功

2. **消息功能 (5-10)**
   - 发送文本消息
   - 接收消息
   - 消息送达状态
   - 发送图片
   - 发送文件
   - 消息历史同步

3. **聊天功能 (11-16)**
   - 创建群聊
   - 添加群成员
   - 群消息广播
   - 已读回执
   - 输入指示器
   - 消息搜索

4. **性能测试 (17-20)**
   - 启动时间 <3s
   - 内存 <200MB
   - 消息延迟 <500ms
   - 滚动性能

5. **稳定性测试 (21-24)**
   - 后台/前台切换
   - 网络切换
   - 长会话 (1 小时)
   - 崩溃恢复

## 🔧 配置

### Gateway 配置 (automation/config/gateway.yaml)

```yaml
gateway:
  primary: "ws://38.226.195.166:18789"
  backup: "ws://xbpd102.cc.cd/ws"
  token: "65a74dc1bcb9e46199acea55909f917069033fe7b749d0abcffc01836b1d10fb"
```

### GitHub 配置

```yaml
github:
  repo: "https://github.com/xiangbianpangde/openclaw-im-client"
  token: "ghp_..."
```

## 📊 运行测试

### 完整测试套件
```bash
cd automation
python3 -m pytest tests/test_openclaw_im.py -v --html=reports/report.html
```

### 单个测试
```bash
python3 -m pytest tests/test_openclaw_im.py::TestOpenClawIM::test_01_app_launch -v
```

### 分析结果
```bash
python3 scripts/analyze_tests.py
```

## 🔄 自循环开发

开发循环自动执行:
1. 分析上次测试报告
2. 识别失败用例
3. 生成修复建议
4. 编译新 APK
5. 运行测试
6. 提交结果到 GitHub

## ⚠️ 常见问题

### 磁盘空间不足
```bash
# 清理 Gradle 缓存
rm -rf /root/.gradle/caches/

# 清理旧 emulator
avdmanager delete avd -n <name>
```

### Appium 连接失败
```bash
# 重启 Appium
pkill -f appium
appium --address 127.0.0.1 --port 4723 &
```

### Emulator 启动失败
```bash
# 检查 emulator 列表
emulator -list-avds

# 创建新 emulator
avdmanager create avd -n test -k "system-images;android-34;default;x86_64" -d pixel_4
```

## 📈 监控

测试报告生成在: `automation/reports/`
日志文件在：`automation/logs/`

---

**版本**: 1.0.0
**最后更新**: 2026-03-30
