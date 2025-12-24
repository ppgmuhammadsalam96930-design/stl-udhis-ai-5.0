# =====================================================
# backend_7py — SUPPORT & OWNERSHIP MONITOR (FINAL)
# ROLE :
#   A. Manual Support (Forgot Password)
#   B. Ownership Claim Monitor (Email Gate PRO)
# PORT : 8007
# =====================================================

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="NajibDev Support & Ownership Monitor")

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SUPPORT_LOG = os.path.join(LOG_DIR, "support_forgot_password.log")
OWNERSHIP_LOG = os.path.join(LOG_DIR, "ownership_claim.log")

EMAIL_RECIPIENTS = [
    "najibsalam23@gmail.com",
    "najibwahidussalam938@gmail.com",
    "ikhsanfakhrozi12@gmail.com"
]

# =========================
# MODELS
# =========================

class SupportPayload(BaseModel):
    message: str
    userAgent: str | None = None
    time: int | None = None

class OwnershipPayload(BaseModel):
    email: str | None = None
    verified: bool = True
    userAgent: str | None = None
    time: int | None = None

# =========================
# UTIL
# =========================

def log_event(path: str, data: dict):
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **data
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print("📝 LOG:", entry)

# =====================================================
# A. SUPPORT — FORGOT PASSWORD (SIDEBAR → HUBUNGI)
# =====================================================

@app.post("/support/forgot-password")
def support_forgot_password(payload: SupportPayload):
    log_event(SUPPORT_LOG, {
        "channel": "SIDEBAR_SUPPORT",
        "message": payload.message,
        "userAgent": payload.userAgent,
        "time": payload.time
    })

    return {
        "status": "received",
        "route": "support/forgot-password",
        "action": "manual_support_required",
        "notify": {
            "whatsapp": "frontend_deeplink",
            "email_targets": EMAIL_RECIPIENTS
        }
    }

# =====================================================
# B. OWNERSHIP — EMAIL GATE PRO (VERIFY / UNLOCK)
# =====================================================

@app.post("/ownership/verified")
def ownership_verified(payload: OwnershipPayload):
    log_event(OWNERSHIP_LOG, {
        "channel": "EMAIL_GATE_PRO",
        "verified": payload.verified,
        "email": payload.email,
        "userAgent": payload.userAgent,
        "time": payload.time
    })

    return {
        "status": "logged",
        "route": "ownership/verified",
        "note": "ownership_claim_recorded_only"
    }

# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "backend_7py",
        "channels": [
            "support_forgot_password",
            "ownership_verified"
        ]
    }

# =====================================================
# RUN
# =====================================================
# uvicorn backend_7py:app --host 127.0.0.1 --port 8007
