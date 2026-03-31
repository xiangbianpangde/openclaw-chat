# GitHub Webhook 处理器
# 当 MAS 仓库有更新时触发 README 同步检查

const http = require('http');
const crypto = require('crypto');
const { execSync } = require('child_process');

const CONFIG = {
  port: process.env.WEBHOOK_PORT || 3000,
  secret: process.env.WEBHOOK_SECRET || 'mas-monitor-secret',
  repo: 'xiangbianpangde/MAS',
  syncScript: '/root/.openclaw/workspace-taizi/mas-monitor/scripts/sync-readme.sh'
};

class GitHubWebhookHandler {
  constructor() {
    this.server = null;
  }

  verifySignature(payload, signature) {
    const expected = 'sha256=' + crypto
      .createHmac('sha256', CONFIG.secret)
      .update(payload)
      .digest('hex');
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expected)
    );
  }

  handleWebhook(req, res) {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', () => {
      try {
        const signature = req.headers['x-hub-signature-256'];
        const event = req.headers['x-github-event'];
        const delivery = req.headers['x-github-delivery'];

        console.log(`📬 Webhook 收到:`);
        console.log(`   Event: ${event}`);
        console.log(`   Delivery: ${delivery}`);

        // 验证签名
        if (signature && !this.verifySignature(body, signature)) {
          console.log('❌ 签名验证失败');
          res.writeHead(401);
          res.end('Invalid signature');
          return;
        }

        const payload = JSON.parse(body);

        // 只处理 push 事件
        if (event !== 'push') {
          console.log('⏭️  非 push 事件，跳过');
          res.writeHead(200);
          res.end('OK');
          return;
        }

        // 检查是否是目标仓库
        const fullName = payload.repository?.full_name;
        if (fullName !== CONFIG.repo) {
          console.log(`⏭️  非目标仓库 (${fullName})，跳过`);
          res.writeHead(200);
          res.end('OK');
          return;
        }

        console.log(`✅ 触发 README 同步检查...`);
        
        // 异步执行同步脚本
        setTimeout(() => {
          try {
            execSync(`bash ${CONFIG.syncScript}`, {
              stdio: 'inherit',
              env: { ...process.env, GH_TOKEN: process.env.GH_TOKEN }
            });
          } catch (error) {
            console.error('❌ 同步脚本执行失败:', error.message);
          }
        }, 0);

        res.writeHead(200);
        res.end('OK');

      } catch (error) {
        console.error('❌ Webhook 处理错误:', error.message);
        res.writeHead(500);
        res.end('Error');
      }
    });
  }

  start() {
    this.server = http.createServer((req, res) => {
      if (req.method === 'POST' && req.url === '/webhook/github') {
        this.handleWebhook(req, res);
      } else {
        res.writeHead(404);
        res.end('Not Found');
      }
    });

    this.server.listen(CONFIG.port, () => {
      console.log(`🚀 GitHub Webhook 服务器已启动`);
      console.log(`   端口：${CONFIG.port}`);
      console.log(`   路径：/webhook/github`);
      console.log(`   目标仓库：${CONFIG.repo}`);
    });
  }

  stop() {
    if (this.server) {
      this.server.close();
      console.log('🛑 Webhook 服务器已停止');
    }
  }
}

// 启动服务
if (require.main === module) {
  const handler = new GitHubWebhookHandler();
  handler.start();
  
  // 优雅关闭
  process.on('SIGINT', () => handler.stop());
  process.on('SIGTERM', () => handler.stop());
}

module.exports = GitHubWebhookHandler;
