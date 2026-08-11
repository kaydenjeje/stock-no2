import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "user_state.json")

DEFAULT_STATE = {
    "onboarded": False,
    "level": None,
    "plan": "free",
    "watchlist": [],
    "journal": [],
    "alert_settings": {"ma_cross": True, "volume": True, "flow": False},
}


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_STATE, **data}
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
