sessions = {}

ROLE_MAP = {
    "1": "Farmer",
    "2": "Seller",
    "3": "Mixed",
    "farmer": "Farmer",
    "seller": "Seller",
    "mixed": "Mixed"
}

INTENT_MAP = {
    "1": "Profit",
    "2": "Emergency",
    "3": "Clearing",
    "4": "Info",
    "profit": "Profit",
    "emergency": "Emergency",
    "clearing": "Clearing",
    "info": "Info"
}

def reset(user_id):
    sessions[user_id] = {
        "stage": 1,
        "data": {}
    }

def get(user_id):
    if user_id not in sessions:
        reset(user_id)
    return sessions[user_id]

def normalize(message, mapping):
    key = message.strip().lower()
    return mapping.get(key, message)

def handle(user_id, message):
    state = get(user_id)

    if message.lower() in ["restart", "anza upya"]:
        reset(user_id)
        return "We start again. Choose your role:\n1. Farmer\n2. Seller\n3. Mixed"

    if state["stage"] == 1:
        state["data"]["type"] = normalize(message, ROLE_MAP)
        state["stage"] = 2
        return "Why are you selling?\n1. Profit\n2. Emergency\n3. Clearing\n4. Info"

    if state["stage"] == 2:
        state["data"]["intent"] = normalize(message, INTENT_MAP)
        state["stage"] = 3
        return "Una nini na uko wapi? (e.g., 50kg tomatoes in Mombasa)"

    if state["stage"] == 3:
        state["data"]["goods"] = message
        state["stage"] = "done"
        return state["data"]
