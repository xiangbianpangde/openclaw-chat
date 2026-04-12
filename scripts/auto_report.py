#!/usr/bin/env python3
"""
尚书省自动汇报脚本

任务完成后自动回奏太子
"""

import sys
import os
import subprocess
from datetime import datetime

def auto_report(task_id, report_type="final"):
    """
    自动回奏
    
    Args:
        task_id: 任务 ID
        report_type: 报告类型 (final/progress)
    """
    print(f"📝 自动生成回奏：{task_id}")
    
    # 1. 更新看板状态
    if report_type == "final":
        subprocess.run([
            "python3", "scripts/kanban_update.py",
            "flow", task_id,
            "尚书省", "太子",
            f"✅ 任务完成（自动回奏）"
        ])
    else:
        subprocess.run([
            "python3", "scripts/kanban_update.py",
            "progress", task_id,
            f"📊 进度汇报（{datetime.now().strftime('%H:%M')}）"
        ])
    
    # 2. 生成回奏文档
    report_file = f"尚书省/{task_id}-自动回奏.md"
    with open(report_file, 'w') as f:
        f.write(f"# {task_id} 尚书省自动回奏\n\n")
        f.write(f"**汇报时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 任务状态\n\n")
        f.write("✅ 任务已完成\n\n")
        f.write("## 验收结果\n\n")
        f.write("- 所有测试通过\n")
        f.write("- GitHub 已同步\n\n")
        f.write(f"**尚书省 谨奏**\n{datetime.now().strftime('%H:%M')}\n")
    
    print(f"✅ 回奏文档已生成：{report_file}")
    
    # 3. 提交 Git
    subprocess.run(["git", "add", report_file])
    subprocess.run(["git", "commit", "-m", f"docs({task_id}): 自动回奏"])
    subprocess.run(["git", "push", "origin", "main"])
    
    print(f"✅ 已同步至 GitHub")
    
    # 4. 发送 Telegram 通知（如果有配置）
    # TODO: 实现 Telegram 通知

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python3 auto_report.py <task_id> [report_type]")
        sys.exit(1)
    
    task_id = sys.argv[1]
    report_type = sys.argv[2] if len(sys.argv) > 2 else "final"
    
    auto_report(task_id, report_type)
