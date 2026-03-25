/**
 * OpenClaw Chat - OpenIM 集成扩展
 * 
 * 功能：
 * - Webhook 接收 OpenIM 消息
 * - 转发到 OpenClaw 处理
 * - 返回响应到 OpenIM
 */

const axios = require('axios');
const express = require('express');

class OpenIMIntegration {
  constructor(config) {
    this.config = {
      serverUrl: config.serverUrl || 'http://localhost:10002',
      botUserId: config.botUserId || 'openclaw_bot',
      adminToken: config.adminToken,
      openclawUrl: config.openclawUrl || 'http://localhost:18789',
    };
    
    this.api = axios.create({
      baseURL: this.config.serverUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // 获取管理员 Token
  async getAdminToken() {
    if (this.config.adminToken) {
      return this.config.adminToken;
    }
    
    const response = await this.api.post('/auth/user_token', {
      userID: 'admin',
      secret: 'openIM123',
    });
    
    return response.data.userToken;
  }

  // 发送消息
  async sendMessage(userId, content, contentType = 101) {
    const token = await this.getAdminToken();
    const operationID = Date.now().toString();
    
    const payload = {
      recvID: userId,
      sendID: this.config.botUserId,
      senderPlatformID: 1,
      contentType: contentType,
      content: JSON.stringify({ content }),
      sessionType: 1, // 单聊
    };

    const response = await this.api.post('/msg/send_msg', payload, {
      headers: {
        operationID,
        token,
      },
    });

    return response.data;
  }

  // 发送图片
  async sendImage(userId, imageUrl) {
    return this.sendMessage(userId, JSON.stringify({
      sourcePicture: { url: imageUrl },
    }), 102);
  }

  // 处理 Webhook
  async handleWebhook(data) {
    const { command, data: msgData } = data;
    
    if (command !== 'afterRecvMsg') {
      return { success: true };
    }

    const { sendID, content, contentType } = msgData;
    
    // 只处理发给机器人的消息
    if (msgData.recvID !== this.config.botUserId) {
      return { success: true };
    }

    try {
      // 解析消息内容
      let messageText = content;
      if (typeof content === 'string') {
        try {
          const parsed = JSON.parse(content);
          messageText = parsed.content || content;
        } catch {
          // 非 JSON 格式，直接使用
        }
      }

      // 转发到 OpenClaw 处理
      const openclawResponse = await this.processWithOpenClaw(sendID, messageText);
      
      // 发送回复
      if (openclawResponse) {
        await this.sendMessage(sendID, openclawResponse);
      }

      return { success: true };
    } catch (error) {
      console.error('处理消息失败:', error);
      await this.sendMessage(sendID, '❌ 处理失败，请稍后重试');
      return { success: false, error: error.message };
    }
  }

  // 调用 OpenClaw API
  async processWithOpenClaw(userId, message) {
    try {
      // 调用 OpenClaw Gateway
      const response = await axios.post(`${this.config.openclawUrl}/agent/turn`, {
        userId,
        message,
        agentId: 'taizi',
      }, {
        timeout: 30000,
      });

      return response.data.response || response.data.message;
    } catch (error) {
      console.error('OpenClaw 调用失败:', error.message);
      
      // 降级响应
      if (message.toLowerCase().includes('help') || message === '/help') {
        return this.getHelpMessage();
      }
      
      return null;
    }
  }

  // 帮助消息
  getHelpMessage() {
    return `🤖 OpenClaw 助手

可用命令：
  /scan     - 扫码登录
  /status   - 查看系统状态
  /desktop  - 远程桌面
  /help     - 显示帮助

直接发送消息也可对话。`;
  }
}

// Express 服务器
function createWebhookServer(integration) {
  const app = express();
  app.use(express.json());

  // Webhook 端点
  app.post('/webhook/openim', async (req, res) => {
    try {
      const result = await integration.handleWebhook(req.body);
      res.json(result);
    } catch (error) {
      console.error('Webhook 错误:', error);
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // 健康检查
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  return app;
}

module.exports = {
  OpenIMIntegration,
  createWebhookServer,
};
