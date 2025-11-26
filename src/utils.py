import uuid


def get_or_create_session_id(session_state):
    if "session_id" not in session_state:
        session_state["session_id"] = str(uuid.uuid4())
    return session_state["session_id"]
