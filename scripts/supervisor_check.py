#!/usr/bin/env python3
"""
太子监督脚本

每 15 分钟检查任务进度，检测汇报延迟
"""

import schedule
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE / "scripts"
KANBAN_CMD = SCRIPTS_DIR / "kanban_update.py"
KANBAN_FILE = WORKSPACE / "kanban.json"
REPORT_DELAY_THRESHOLD = 10  # 汇报延迟阈值（分钟）

def check_progress():
    """
    检查任务进度
    """
    print(f"\n🔍 太子监督检查：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 读取看板数据
    if not KANBAN_FILE.exists():
        print("❌ 看板文件不存在")
        return
    
    with open(KANBAN_FILE, 'r', encoding='utf-8') as f:
        kanban_data = json.load(f)
    
    tasks = kanban_data.get('tasks', {})
    
    # 2. 检查每个任务
    delayed_tasks = []
    
    for task_id, task in tasks.items():
        # 检查任务状态
        status = task.get('state', '')
        flow_history = task.get('flow_history', [])
        
        # 检查是否有延迟
        if is_task_delayed(task, flow_history):
            delayed_tasks.append({
                'task_id': task_id,
                'title': task.get('title', ''),
                'status': status
            })
    
    # 3. 处理延迟任务
    if delayed_tasks:
        print(f"\n⚠️ 发现 {len(delayed_tasks)} 个延迟任务:")
        for task in delayed_tasks:
            print(f"  - {task['task_id']}: {task['title']}")
            send_reminder(task['task_id'], task['title'])
    else:
        print("\n✅ 所有任务正常")
    
    # 4. 记录监督结果
    record_supervision(len(delayed_tasks))

def is_task_delayed(task, flow_history):
    """
    检查任务是否延迟
    
    Args:
        task: 任务数据
        flow_history: 流程历史
    
    Returns:
        bool: 是否延迟
    """
    # 获取最后更新时间
    if not flow_history:
        return False
    
    last_update = flow_history[-1].get('time', '')
    
    try:
        last_update_time = datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        delay = (now - last_update_time).total_seconds() / 60  # 分钟
        
        # 如果超过 15 分钟未更新，视为延迟
        return delay > 15
    except:
        return False

def send_reminder(task_id: str, task_title: str):
    """
    发送催办通知
    
    Args:
        task_id: 任务 ID
        task_title: 任务标题
    """
    print(f"\n📢 发送催办通知：{task_id}")
    
    # 1. 更新看板标记
    subprocess.run([
        "python3", str(KANBAN_CMD),
        "progress", task_id,
        f"⚠️ 太子催办（{datetime.now().strftime('%H:%M')}）"
    ], cwd=WORKSPACE)
    
    # 2. 发送 Telegram 通知
    send_telegram_reminder(task_id, task_title)

def send_telegram_reminder(task_id: str, task_title: str):
    """
    发送 Telegram 催办通知
    
    Args:
        task_id: 任务 ID
        task_title: 任务标题
    """
    config_file = WORKSPACE / "config" / "telegram.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        bot_token = config.get('bot_token')
        chat_id = config.get('chat_id')
        
        if bot_token and chat_id:
            # 催办消息
            message = f"""
⚠️ 太子催办

任务：{task_id}
标题：{task_title}
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

状态：⚠️ 汇报延迟
要求：请立即回奏！
"""
            # TODO: 调用 Telegram API 发送消息
            print(f"✅ Telegram 催办通知已发送（模拟）")
        else:
            print(f"⚠️ Telegram 配置不完整，跳过通知")
    else:
        print(f"⚠️ Telegram 配置文件不存在，跳过通知")

def record_supervision(delayed_count: int):
    """
    记录监督结果
    
    Args:
        delayed_count: 延迟任务数
    """
    record_file = WORKSPACE / "太子" / "监督记录.md"
    
    # 追加记录
    with open(record_file, 'a', encoding='utf-8') as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"- 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 延迟任务：{delayed_count} 个\n")
        f.write(f"- 状态：{'有延迟' if delayed_count > 0 else '正常'}\n")
    
    print(f"📝 监督记录已更新：{record_file}")

def main():
    """
    主函数
    """
    print("=" * 60)
    print("👑 太子监督服务启动")
    print("=" * 60)
    print(f"工作目录：{WORKSPACE}")
    print(f"检查频率：每 15 分钟")
    print(f"延迟阈值：{REPORT_DELAY_THRESHOLD} 分钟")
    print("=" * 60)
    
    # 立即执行一次检查
    check_progress()
    
    # 设置定时任务
    schedule.every(15).minutes.do(check_progress)
    
    print("\n✅ 监督服务运行中...")
    print("按 Ctrl+C 停止")
    
    # 运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 监督服务已停止")

if __name__ == "__main__":
    main()
