from datetime import datetime, timedelta

sessions = {}

MAX_HISTORY = 10
SESSION_TIMEOUT = 30  


def get_session(user_id):

    now = datetime.utcnow()

    if user_id not in sessions:
        sessions[user_id] = {
            "intent": None,
            "history": [],
            "last_active": now
        }

    session = sessions[user_id]

    if now - session["last_active"] > timedelta(minutes=SESSION_TIMEOUT):
        sessions[user_id] = {
            "intent": None,
            "history": [],
            "last_active": now
        }
        return sessions[user_id]

    session["last_active"] = now

    if len(session["history"]) > MAX_HISTORY:
        session["history"] = session["history"][-MAX_HISTORY:]

    return session


def reset_session(user_id):

    sessions[user_id] = {
        "intent": None,
        "history": [],
        "last_active": datetime.utcnow()
    }