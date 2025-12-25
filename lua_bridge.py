# lua_bridge.py
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)

with open("instinct.lua", "r", encoding="utf-8") as f:
    instinct = lua.execute(f.read())

def apply_instinct(mode: str, core_response: str) -> str:
    return instinct.respond(mode, core_response)
