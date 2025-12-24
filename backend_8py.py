# =====================================================
# backend_8py — SUPREME POLICY AUTHORITY (NAJIBDEV)
# ROLE : Final Law / Enforcement / Signature Authority
# MODE : READ-ONLY POLICY + AUDIT
# =====================================================

import hmac
import hashlib
import time
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===============================
# CONFIG
# ===============================

SECRET_KEY = b"NAJIBDEV_SUPREME_LAW_V1"
BACKEND_6 = "http://127.0.0.1:8006/policy"

app = FastAPI(title="NajibDev Supreme Policy Authority")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ===============================
# UTIL
# ===============================

def sign(payload: str) -> str:
    return hmac.new(
        SECRET_KEY,
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

# ===============================
# POLICY AGGREGATOR
# ===============================

@app.get("/policy/final")
def final_policy():
    # 1. Ambil policy runtime dari backend_6
    try:
        base = requests.get(BACKEND_6, timeout=1).json()
    except:
        base = {
            "global_mode": "LOCKDOWN",
            "ui_policy": "locked",
            "vault_access": False,
            "game_quality": "minimal",
            "locks": {"username": True, "danger_zone": True}
        }

    # 2. Tambah enforcement keras
    final = {
        "authority": "najibdev",
        "issued_at": int(time.time()),
        "enforcement": "HARD",
        "policy": base,
        "rules": {
            "ui_must_obey": True,
            "ignore_policy": "force_downgrade",
            "tamper_detect": True
        }
    }

    # 3. Signature (anti-spoof)
    payload = str(final)
    final["signature"] = sign(payload)

    return final
