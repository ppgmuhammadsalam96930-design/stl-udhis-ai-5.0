# =====================================================
# BACKEND_6PY — GLOBAL GOVERNOR & WATCHDOG (FINAL)
# ROLE : Silent Runtime Controller + Policy Authority
# MODE : DAEMON / READ-ONLY API
# =====================================================

import time
import threading
import psutil
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =====================================================
# FASTAPI (READ-ONLY)
# =====================================================

app = FastAPI(title="Global Governor Policy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local UI only
    allow_methods=["GET"],
    allow_headers=["*"],
)

# =====================================================
# GLOBAL STATE (SINGLE SOURCE OF TRUTH)
# =====================================================

STATE = {
    "mode": "NORMAL",            # NORMAL | THROTTLE | DEGRADED | LOCKDOWN
    "last_check": 0,
    "ui_policy": "auto",         # auto | balanced | low | locked
    "vault_access": True,
    "game_quality": "high",      # high | medium | minimal
    "locks": {
        "username": False,
        "danger_zone": False
    }
}

# =====================================================
# BACKEND DEPENDENCIES
# =====================================================

BACKENDS = {
    "edu": "http://127.0.0.1:5000/health",
    "vault": "http://127.0.0.1:8001/health",
    "akasha": "http://127.0.0.1:8004/health",
    "persona": "http://127.0.0.1:8010/health",
    "ui": "http://127.0.0.1:8003/health"
}

# =====================================================
# HEALTH CHECK
# =====================================================

def ping(url, timeout=1):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except:
        return False

# =====================================================
# DECISION ENGINE (PURE LOGIC)
# =====================================================

def decide(cpu, mem, backend_status):
    if not backend_status.get("vault", True):
        return "LOCKDOWN"
    if mem > 85 or cpu > 90:
        return "DEGRADED"
    if cpu > 70:
        return "THROTTLE"
    return "NORMAL"

# =====================================================
# POLICY APPLICATION
# =====================================================

def apply_policies(mode):
    if mode == "LOCKDOWN":
        STATE.update({
            "ui_policy": "locked",
            "vault_access": False,
            "game_quality": "minimal",
            "locks": {
                "username": True,
                "danger_zone": True
            }
        })

    elif mode == "DEGRADED":
        STATE.update({
            "ui_policy": "low",
            "vault_access": False,
            "game_quality": "medium",
            "locks": {
                "username": False,
                "danger_zone": True
            }
        })

    elif mode == "THROTTLE":
        STATE.update({
            "ui_policy": "balanced",
            "vault_access": True,
            "game_quality": "high",
            "locks": {
                "username": False,
                "danger_zone": False
            }
        })

    else:  # NORMAL
        STATE.update({
            "ui_policy": "auto",
            "vault_access": True,
            "game_quality": "high",
            "locks": {
                "username": False,
                "danger_zone": False
            }
        })

# =====================================================
# GOVERNOR LOOP (DAEMON THREAD)
# =====================================================

def governor_loop():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent

        backend_status = {k: ping(v) for k, v in BACKENDS.items()}
        mode = decide(cpu, mem, backend_status)

        STATE["mode"] = mode
        STATE["last_check"] = time.time()

        apply_policies(mode)

        time.sleep(2)

# =====================================================
# READ-ONLY POLICY ENDPOINT (FOR UI)
# =====================================================

@app.get("/policy")
def get_policy():
    """
    READ-ONLY.
    UI boleh membaca, tidak bisa mengubah.
    """
    return {
        "global_mode": STATE["mode"],
        "ui_policy": STATE["ui_policy"],
        "vault_access": STATE["vault_access"],
        "game_quality": STATE["game_quality"],
        "locks": STATE["locks"],
        "last_check": STATE["last_check"]
    }

# =====================================================
# BOOT
# =====================================================

threading.Thread(target=governor_loop, daemon=True).start()

print("🛡️ backend_6.py GOVERNOR ACTIVE (silent + policy mode)")

# Jalankan dengan:
# uvicorn backend_6py:app --host 127.0.0.1 --port 8006
