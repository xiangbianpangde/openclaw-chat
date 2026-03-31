#!/usr/bin/env node
/**
 * MAS Monitor - 主监控程序
 * 整合所有分析模块，实现 5 分钟轮询
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = require('./config/agent-config.json');

const CodeArchitectureAnalyzer = require('./scripts/analyze-architecture');
const ChangelogTracker = require('./scripts/track-changelog');
const DependencyAnalyzer = require('./scripts/analyze-dependencies');
const MajorChangeDetector = require('./scripts/detect-major-changes');
const ContextCompressor = require('./scripts/context-compressor');

class MASMonitor {
  constructor() {
    this.config = CONFIG;
    this.running = false;
    this.pollInterval = CONFIG.github.pollIntervalMinutes * 60 * 1000;
  }

  async start() {
    console.log('🚀 MAS Monitor 启动...');
    console.log(`📊 目标仓库：${this.config.github.targetRepo}`);
    console.log(`⏱️ 轮询间隔：${this.config.github.pollIntervalMinutes} 分钟`);
    console.log(`🤖 模型配置:`);
    console.log(`   - 默认：${this.config.models.default}`);
    console.log(`   - 代码分析：${this.config.models.codeAnalysis}`);
    console.log(`   - 变更检测：${this.config.models.changeDetection}`);
    
    this.running = true;
    await this.runAnalysisCycle();
    
    // 启动轮询
    if (this.running) {
      console.log('⏰ 启动定时轮询...');
      setInterval(() => this.runAnalysisCycle(), this.pollInterval);
    }
  }

  async runAnalysisCycle() {
    console.log('\n' + '='.repeat(60));
    console.log(`📈 开始分析周期：${new Date().toISOString()}`);
    console.log('='.repeat(60));

    try {
      // 1. 快速变更检测 (qwen-turbo)
      console.log('\n[1/4] ⚡ 快速变更检测...');
      const changeDetector = new (require('./scripts/detect-major-changes'))();
      const changes = await changeDetector.detect();

      // 2. 更新日志跟踪 (qwen-plus)
      console.log('\n[2/4] 📝 更新日志跟踪...');
      const changelogTracker = new (require('./scripts/track-changelog'))();
      const changelog = await changelogTracker.track();

      // 3. 依赖分析 (qwen-coder-plus)
      console.log('\n[3/4] 📦 依赖关系分析...');
      const depAnalyzer = new (require('./scripts/analyze-dependencies'))();
      const dependencies = await depAnalyzer.analyze();

      // 4. 代码架构分析 (qwen-coder-plus)
      console.log('\n[4/4] 🔍 代码架构分析...');
      const archAnalyzer = new (require('./scripts/analyze-architecture'))();
      const architecture = await archAnalyzer.analyze();

      // 5. 上下文压缩
      console.log('\n🗜️ 执行上下文压缩...');
      const compressor = new (require('./scripts/context-compressor'))();
      await compressor.runFullCompressionCycle();

      // 6. 生成综合报告
      console.log('\n📊 生成综合报告...');
      await this.generateSummaryReport({
        changes,
        changelog,
        dependencies,
        architecture
      });

      console.log('\n✅ 分析周期完成');
      
    } catch (error) {
      console.error('❌ 分析周期失败:', error.message);
    }
  }

  async generateSummaryReport(data) {
    const report = {
      timestamp: new Date().toISOString(),
      agent: this.config.agent.name,
      version: this.config.agent.version,
      targetRepo: this.config.github.targetRepo,
      summary: {
        breakingChanges: data.changes.breaking.length,
        newFeatures: data.changes.features.length,
        riskLevel: data.changes.riskLevel,
        dependenciesUpdated: data.dependencies.updates?.length || 0
      },
      details: data
    };

    const reportPath = path.join(__dirname, 'reports/realtime/summary.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 综合报告：${reportPath}`);

    return report;
  }

  stop() {
    this.running = false;
    console.log('🛑 MAS Monitor 已停止');
  }
}

// CLI interface
if (require.main === module) {
  const monitor = new MASMonitor();
  
  if (process.argv.includes('--once')) {
    monitor.runAnalysisCycle().catch(console.error);
  } else {
    monitor.start().catch(console.error);
  }
}

module.exports = MASMonitor;
