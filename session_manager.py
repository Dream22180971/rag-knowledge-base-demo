"""
多会话状态：新对话、切换历史、本地 JSON 持久化（按用户名分文件，演示级）。
"""
from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _path_for_user(username: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in username)[:64]
    return os.path.join(DATA_DIR, f"sessions_{safe}.json")


def load_user_sessions(username: str) -> Dict[str, Any]:
    path = _path_for_user(username)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_user_sessions(username: str, payload: Dict[str, Any]) -> None:
    path = _path_for_user(username)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def bootstrap_sessions(session_state, username: str) -> None:
    """从磁盘恢复或初始化会话树。"""
    raw = load_user_sessions(username)
    sessions = raw.get("sessions")
    cur = raw.get("current_session_id")

    if not sessions:
        sid = str(uuid.uuid4())
        sessions = {
            sid: {
                "title": "新对话",
                "messages": [],
                "updated": datetime.now().isoformat(timespec="seconds"),
                "created": datetime.now().isoformat(timespec="seconds"),
            }
        }
        cur = sid

    session_state.chat_sessions = sessions
    session_state.current_session_id = cur if cur in sessions else next(iter(sessions))
    session_state.messages = deepcopy(
        sessions[session_state.current_session_id].get("messages", [])
    )


def persist_from_streamlit(session_state, username: str) -> None:
    """把当前 session_state 写回磁盘。"""
    sid = session_state.current_session_id
    if sid not in session_state.chat_sessions:
        return
    session_state.chat_sessions[sid]["messages"] = deepcopy(session_state.messages)
    # 标题：首条用户问题摘要
    title = "新对话"
    for m in session_state.messages:
        if m.get("role") == "user" and (m.get("content") or "").strip():
            title = (m["content"].strip())[:40]
            if len(m["content"]) > 40:
                title += "…"
            break
    session_state.chat_sessions[sid]["title"] = title
    session_state.chat_sessions[sid]["updated"] = datetime.now().isoformat(
        timespec="seconds"
    )
    payload = {
        "current_session_id": sid,
        "sessions": session_state.chat_sessions,
    }
    save_user_sessions(username, payload)


def new_conversation(session_state) -> None:
    persist_from_streamlit(session_state, session_state.username)
    sid = str(uuid.uuid4())
    session_state.chat_sessions[sid] = {
        "title": "新对话",
        "messages": [],
        "updated": datetime.now().isoformat(timespec="seconds"),
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    session_state.current_session_id = sid
    session_state.messages = []


def switch_session(session_state, username: str, target_sid: str) -> None:
    if target_sid == session_state.current_session_id:
        return
    persist_from_streamlit(session_state, username)
    session_state.current_session_id = target_sid
    session_state.messages = deepcopy(
        session_state.chat_sessions[target_sid].get("messages", [])
    )


def ordered_session_ids(session_state) -> List[str]:
    items = list(session_state.chat_sessions.items())
    items.sort(key=lambda x: x[1].get("updated", ""), reverse=True)
    return [k for k, _ in items]


def session_label(session_state, sid: str) -> str:
    d = session_state.chat_sessions.get(sid, {})
    t = d.get("title", "未命名")
    u = (d.get("updated") or "")[:16].replace("T", " ")
    return f"{t} · {u}"
