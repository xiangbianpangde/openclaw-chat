#!/usr/bin/env node
/**
 * MAS 重大变更检测脚本
 * 使用 qwen-turbo 快速检测重大变更
 */

const fs = require('fs');
const path = require('path');

const CONFIG = require('../config/agent-config.json');

class MajorChangeDetector {
  constructor() {
    this.repo = CONFIG.github.targetRepo;
    this.outputDir = path.join(__dirname, '../reports/realtime');
    this.lastCheckFile = path.join(__dirname, '../config/last-check.json');
  }

  async detect() {
    console.log('⚡ 开始重大变更检测...');
    
    const lastCheck = this.loadLastCheck();
    const changes = {
      timestamp: new Date().toISOString(),
      model: CONFIG.models.changeDetection,
      since: lastCheck.timestamp,
      breaking: [],
      features: [],
      fixes: [],
      docs: [],
      riskLevel: 'low'
    };

    // 检测重大变更
    changes.breaking = await this.detectBreakingChanges(lastCheck);
    changes.riskLevel = this.assessRisk(changes);

    this.saveReport('major-changes.json', changes);
    this.saveLastCheck({ timestamp: changes.timestamp });

    return changes;
  }

  loadLastCheck() {
    if (fs.existsSync(this.lastCheckFile)) {
      return JSON.parse(fs.readFileSync(this.lastCheckFile, 'utf8'));
    }
    return { timestamp: new Date(Date.now() - 86400000).toISOString() }; // 默认 24 小时前
  }

  saveLastCheck(data) {
    fs.writeFileSync(this.lastCheckFile, JSON.stringify(data, null, 2));
  }

  async detectBreakingChanges(lastCheck) {
    // 检测破坏性变更
    // - API 变更
    // - 配置格式变更
    // - 依赖重大版本更新
    return [];
  }

  assessRisk(changes) {
    if (changes.breaking.length > 0) return 'high';
    if (changes.features.length > 5) return 'medium';
    return 'low';
  }

  saveReport(filename, data) {
    const filepath = path.join(this.outputDir, filename);
    fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
    console.log(`📄 报告已保存：${filepath}`);
  }
}

if (require.main === module) {
  const detector = new MajorChangeDetector();
  detector.detect().catch(console.error);
}

module.exports = MajorChangeDetector;
