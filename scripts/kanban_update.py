#!/usr/bin/env python3
"""
看板管理 CLI — 太子·三省六部制
用法:
  python3 scripts/kanban_update.py create <id> "<title>" <state> <org> <official> "<remark>"
  python3 scripts/kanban_update.py state  <id> <state> "<remark>"
  python3 scripts/kanban_update.py flow   <id> "<from>" "<to>" "<remark>"
  python3 scripts/kanban_update.py done   <id> "<output>" "<summary>"
  python3 scripts/kanban_update.py progress <id> "<current>" "<plan>"
  python3 scripts/kanban_update.py list   [--state <state>] [--org <org>]
  python3 scripts/kanban_update.py show   <id>
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
KANBAN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kanban.json")


def load_kanban():
    if os.path.exists(KANBAN_FILE):
        with open(KANBAN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": {}, "flow_log": []}


def save_kanban(data):
    with open(KANBAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_str():
    return datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S CST")


def cmd_create(args):
    if len(args) < 6:
        print("用法: create <id> <title> <state> <org> <official> <remark>")
        sys.exit(1)
    task_id, title, state, org, official, remark = args[0], args[1], args[2], args[3], args[4], args[5] if len(args) > 5 else ""
    kb = load_kanban()
    if task_id in kb["tasks"]:
        print(f"❌ 任务 {task_id} 已存在")
        sys.exit(1)
    kb["tasks"][task_id] = {
        "id": task_id,
        "title": title,
        "state": state,
        "org": org,
        "official": official,
        "created_at": now_str(),
        "updated_at": now_str(),
        "progress": {"current": "", "plan": ""},
        "flow_history": [
            {"time": now_str(), "action": "创建", "from": "皇上", "to": org, "remark": remark}
        ],
        "output": "",
        "summary": ""
    }
    kb["flow_log"].append({
        "time": now_str(), "task_id": task_id, "action": "create",
        "detail": f"创建任务: {title} → {org}/{official}"
    })
    save_kanban(kb)
    print(f"✅ 任务 {task_id} 已创建: {title}")
    print(f"   状态: {state} | 部门: {org} | 负责人: {official}")


def cmd_state(args):
    if len(args) < 3:
        print("用法: state <id> <state> <remark>")
        sys.exit(1)
    task_id, state, remark = args[0], args[1], args[2]
    kb = load_kanban()
    if task_id not in kb["tasks"]:
        print(f"❌ 任务 {task_id} 不存在")
        sys.exit(1)
    task = kb["tasks"][task_id]
    old_state = task["state"]
    task["state"] = state
    task["updated_at"] = now_str()
    task["flow_history"].append({
        "time": now_str(), "action": "状态变更",
        "from": old_state, "to": state, "remark": remark
    })
    kb["flow_log"].append({
        "time": now_str(), "task_id": task_id, "action": "state",
        "detail": f"{old_state} → {state}: {remark}"
    })
    save_kanban(kb)
    print(f"✅ 任务 {task_id} 状态: {old_state} → {state}")


def cmd_flow(args):
    if len(args) < 4:
        print("用法: flow <id> <from> <to> <remark>")
        sys.exit(1)
    task_id, frm, to, remark = args[0], args[1], args[2], args[3]
    kb = load_kanban()
    if task_id not in kb["tasks"]:
        print(f"❌ 任务 {task_id} 不存在")
        sys.exit(1)
    task = kb["tasks"][task_id]
    task["updated_at"] = now_str()
    task["flow_history"].append({
        "time": now_str(), "action": "流转",
        "from": frm, "to": to, "remark": remark
    })
    kb["flow_log"].append({
        "time": now_str(), "task_id": task_id, "action": "flow",
        "detail": f"{frm} → {to}: {remark}"
    })
    save_kanban(kb)
    print(f"✅ 任务 {task_id} 流转: {frm} → {to}")
    print(f"   备注: {remark}")


def cmd_done(args):
    if len(args) < 3:
        print("用法: done <id> <output> <summary>")
        sys.exit(1)
    task_id, output, summary = args[0], args[1], args[2]
    kb = load_kanban()
    if task_id not in kb["tasks"]:
        print(f"❌ 任务 {task_id} 不存在")
        sys.exit(1)
    task = kb["tasks"][task_id]
    task["state"] = "已完成"
    task["output"] = output
    task["summary"] = summary
    task["updated_at"] = now_str()
    task["flow_history"].append({
        "time": now_str(), "action": "完成",
        "from": task["org"], "to": "皇上", "remark": f"✅ {summary}"
    })
    kb["flow_log"].append({
        "time": now_str(), "task_id": task_id, "action": "done",
        "detail": f"完成: {summary}"
    })
    save_kanban(kb)
    print(f"✅ 任务 {task_id} 已完成")
    print(f"   产出: {output}")
    print(f"   摘要: {summary}")


def cmd_progress(args):
    if len(args) < 3:
        print("用法: progress <id> <current> <plan>")
        sys.exit(1)
    task_id, current, plan = args[0], args[1], args[2]
    kb = load_kanban()
    if task_id not in kb["tasks"]:
        print(f"❌ 任务 {task_id} 不存在")
        sys.exit(1)
    task = kb["tasks"][task_id]
    task["progress"]["current"] = current
    task["progress"]["plan"] = plan
    task["updated_at"] = now_str()
    save_kanban(kb)
    print(f"📊 任务 {task_id} 进展已更新")
    print(f"   当前: {current}")
    print(f"   计划: {plan}")


def cmd_list(args):
    kb = load_kanban()
    state_filter = None
    org_filter = None
    i = 0
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            state_filter = args[i + 1]
            i += 2
        elif args[i] == "--org" and i + 1 < len(args):
            org_filter = args[i + 1]
            i += 2
        else:
            i += 1

    tasks = kb["tasks"].values()
    if state_filter:
        tasks = [t for t in tasks if t["state"] == state_filter]
    if org_filter:
        tasks = [t for t in tasks if t["org"] == org_filter]

    tasks = sorted(tasks, key=lambda t: t.get("updated_at", ""), reverse=True)

    if not tasks:
        print("📋 看板为空" if not state_filter and not org_filter else "📋 无匹配任务")
        return

    print(f"📋 看板任务列表 (共 {len(tasks)} 项)")
    print("-" * 70)
    for t in tasks:
        progress_str = ""
        if t.get("progress", {}).get("current"):
            progress_str = f"\n     进展: {t['progress']['current']}"
        print(f"  [{t['state']}] {t['id']}: {t['title']}")
        print(f"     部门: {t['org']} | 负责人: {t['official']} | 更新: {t['updated_at']}{progress_str}")
        print()


def cmd_show(args):
    if len(args) < 1:
        print("用法: show <id>")
        sys.exit(1)
    task_id = args[0]
    kb = load_kanban()
    if task_id not in kb["tasks"]:
        print(f"❌ 任务 {task_id} 不存在")
        sys.exit(1)
    task = kb["tasks"][task_id]
    print(f"📋 任务详情: {task_id}")
    print("=" * 60)
    print(f"  标题: {task['title']}")
    print(f"  状态: {task['state']}")
    print(f"  部门: {task['org']}")
    print(f"  负责人: {task['official']}")
    print(f"  创建时间: {task['created_at']}")
    print(f"  更新时间: {task['updated_at']}")
    if task.get("progress", {}).get("current"):
        print(f"  当前进展: {task['progress']['current']}")
    if task.get("progress", {}).get("plan"):
        print(f"  计划: {task['progress']['plan']}")
    if task.get("output"):
        print(f"  产出: {task['output']}")
    if task.get("summary"):
        print(f"  摘要: {task['summary']}")
    print()
    print("  流转历史:")
    for h in task.get("flow_history", []):
        print(f"    [{h['time']}] {h['action']}: {h.get('from', '')} → {h.get('to', '')} | {h.get('remark', '')}")


COMMANDS = {
    "create": cmd_create,
    "state": cmd_state,
    "flow": cmd_flow,
    "done": cmd_done,
    "progress": cmd_progress,
    "list": cmd_list,
    "show": cmd_show,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
