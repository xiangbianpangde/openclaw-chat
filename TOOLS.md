# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Agent Skills 配置

### 已安装 Skills（52 个）

**AI/ML Skills:**
- openai-whisper - 本地语音识别（✅ 可用，无需 API）
- openai-whisper-api - Whisper API（⚠️ 需要 OPENAI_API_KEY）
- gemini - Google Gemini CLI（✅ CLI 可用）
- sag - ElevenLabs TTS（⚠️ 需要 ELEVENLABS_API_KEY）
- summarize - 文本摘要（⚠️ 需要安装 CLI）
- model-usage - 模型监控（⚠️ 需要 codexbar）
- sherpa-onnx-tts - 本地 TTS
- oracle - 查询工具

**开发工具:**
- coding-agent - 编码助手
- github - GitHub 操作
- gh-issues - GitHub Issues
- skill-creator - Skill 创建
- tmux - 终端复用
- video-frames - 视频帧提取

**通讯:**
- discord - Discord 集成
- slack - Slack 集成
- imsg - iMessage
- bluebubbles - BlueBubbles
- voice-call - 语音通话

**笔记:**
- apple-notes - Apple Notes
- apple-reminders - Apple Reminders
- bear-notes - Bear Notes
- notion - Notion
- obsidian - Obsidian

**媒体:**
- camsnap - 相机快照
- gifgrep - GIF 搜索
- songsee - 歌曲识别
- spotify-player - Spotify
- sonoscli - Sonos 控制

**系统工具:**
- healthcheck - 健康检查
- node-connect - 节点连接
- blucli - Bluetooth CLI
- eightctl - 8 球控制
- peekaboo - 隐藏/显示
- mcporter - 端口映射
- ordercli - 订单 CLI
- xurl - URL 工具

**数据:**
- nano-pdf - PDF 处理
- openhue - Hue 灯光
- gog - GOG 游戏
- goplaces - 地点服务

**项目管理:**
- trello - Trello
- things-mac - Things 3
- clawhub - ClawHub
- canvas - Canvas

**其他:**
- blogwatcher - 博客监控
- himalaya - 邮件客户端
- session-logs - 会话日志
- wacli - WhatsApp CLI
- weather - 天气查询
- 1password - 1Password
- chrome-devtools-tester - Chrome DevTools 测试（太子项目）

### API Keys 状态

| API | 状态 | 说明 |
|-----|------|------|
| OpenAI API Key | ❌ 未配置 | 需要配置 OPENAI_API_KEY |
| Google Gemini API Key | ❌ 未配置 | 需要配置 GEMINI_API_KEY |
| ElevenLabs API Key | ❌ 未配置 | 需要配置 ELEVENLABS_API_KEY |

### 可用 Skills（无需 API）

- ✅ openai-whisper (本地)
- ✅ gemini (CLI)
- ✅ github
- ✅ healthcheck
- ✅ weather (wttr.in)
- ✅ chrome-devtools-tester

### 配置说明

**环境变量配置:**
```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export ELEVENLABS_API_KEY="..."
```

**配置文件:** `~/.openclaw/config.json`

---

Add whatever helps you do your job. This is your cheat sheet.
