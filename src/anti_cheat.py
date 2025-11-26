import time
from .config import EXAM_DURATION_SECONDS


def init_anti_cheat_state(session_state):
    if "tab_switch_count" not in session_state:
        session_state["tab_switch_count"] = 0
    if "paste_attempt_count" not in session_state:
        session_state["paste_attempt_count"] = 0
    if "exam_start_ts" not in session_state:
        session_state["exam_start_ts"] = time.time()


def get_exam_features(session_state):
    now = time.time()
    start = session_state.get("exam_start_ts", now)
    durasi = max(0, int(now - start))

    # anti-cheat lebih advanced (JS) bisa ditambahkan kemudian
    return {
        "durasi_detik": durasi,
        "tab_switch_count": session_state.get("tab_switch_count", 0),
        "paste_attempt_count": session_state.get("paste_attempt_count", 0),
    }


def get_time_remaining(session_state):
    now = time.time()
    start = session_state.get("exam_start_ts", now)
    elapsed = now - start
    remaining = max(0, EXAM_DURATION_SECONDS - elapsed)
    return elapsed, remaining
