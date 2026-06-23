import json
import os
import asyncio
from pathlib import Path

# fetcher_core/core/state_manager.py -> fetcher_core/
STATE_FILE = Path(__file__).resolve().parent.parent / "config" / "user_state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Lock global untuk state management
state_lock = asyncio.Lock()


async def load_user_state():
    async with state_lock:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        return {}


async def save_user_state(state):
    async with state_lock:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)


async def set_user_state(user_id, state):
    state_dict = await load_user_state()
    state_dict[str(user_id)] = state
    await save_user_state(state_dict)


async def get_user_state(user_id):
    state = await load_user_state()
    return state.get(str(user_id), None)


async def clear_user_state(user_id):
    state_dict = await load_user_state()
    if str(user_id) in state_dict:
        del state_dict[str(user_id)]
        await save_user_state(state_dict)
