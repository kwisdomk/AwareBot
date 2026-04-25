sessions = {}

def reset(user_id):
    sessions[user_id] = {
        "stage": 1,
        "data": {}
    }

def get(user_id):
    if user_id not in sessions:
        reset(user_id)
    return sessions[user_id]


def handle(user_id, message):
    state = get(user_id)

    if message.lower() in ["restart", "anza upya"]:
        reset(user_id)
        return "We start again. Wewe ni: Farmer / Seller / Mixed"

    if state["stage"] == 1:
        state["data"]["type"] = message
        state["stage"] = 2
        return "Kwa nini unauza? Profit / Emergency / Clearing / Info"

    if state["stage"] == 2:
        state["data"]["intent"] = message
        state["stage"] = 3
        return "Una nini na uko wapi?"

    if state["stage"] == 3:
        state["data"]["goods"] = message
        state["stage"] = "done"
        return state["data"]
