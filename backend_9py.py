# =====================================================
# backend_9py — RUNTIME INFRASTRUCTURE MAINTAINER (FINAL)
# ROLE : Circuit Breaker / Deadlock Resolver / Freeze Manager
# AUTH : NONE (MECHANICAL ONLY)
# MODE : SILENT / NON-INTERACTIVE
# =====================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import hashlib
import os
import json
import time
from typing import Optional

# =========================
# CONFIG
# =========================
FREEZE_HOURS = 24
DATA_DIR = "infra_state"
os.makedirs(DATA_DIR, exist_ok=True)

FREEZE_DB = os.path.join(DATA_DIR, "freeze_table.json")
SEAL_DB   = os.path.join(DATA_DIR, "seal_table.json")  # stores HASHED seals only

# =========================
# APP
# =========================
app = FastAPI(title="NajibDev Runtime Infra Maintainer (backend_9py)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # internal usage recommended
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class FreezeReq(BaseModel):
    path_id: str              # identifier jalur (mis: "router->8005")
    reason: Optional[str] = None
    seal_token: Optional[str] = None  # optional, used ONLY for bypass

class CheckReq(BaseModel):
    path_id: str
    seal_token: Optional[str] = None

class UnfreezeReq(BaseModel):
    path_id: str
    seal_token: str           # najibdev only

# =========================
# UTILS (NO IMEI EVER)
# =========================
def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _hash_token(token: str) -> str:
    # Strong one-way hash; token itself never stored
    return hashlib.sha256(token.encode()).hexdigest()

def _now():
    return int(time.time())

def _is_najibdev(seal_token: Optional[str]) -> bool:
    if not seal_token:
        return False
    seals = _load_json(SEAL_DB, {"najibdev": []})
    return _hash_token(seal_token) in seals.get("najibdev", [])

# =========================
# CORE LOGIC (MECHANICAL)
# =========================
def _freeze_path(path_id: str, hours: int):
    table = _load_json(FREEZE_DB, {})
    until = _now() + int(hours * 3600)
    table[path_id] = {
        "frozen_at": _now(),
        "until": until
    }
    _save_json(FREEZE_DB, table)

def _unfreeze_path(path_id: str):
    table = _load_json(FREEZE_DB, {})
    if path_id in table:
        del table[path_id]
        _save_json(FREEZE_DB, table)

def _check_frozen(path_id: str):
    table = _load_json(FREEZE_DB, {})
    entry = table.get(path_id)
    if not entry:
        return False, None

    if _now() > entry["until"]:
        # auto-thaw
        del table[path_id]
        _save_json(FREEZE_DB, table)
        return False, None

    return True, entry["until"]

# =========================
# ROUTES
# =========================
@app.post("/infra/freeze")
def freeze(req: FreezeReq):
    # najibdev bypass: do nothing
    if _is_najibdev(req.seal_token):
        return {
            "status": "bypassed",
            "note": "najibdev seal detected",
            "path_id": req.path_id
        }

    _freeze_path(req.path_id, FREEZE_HOURS)
    return {
        "status": "frozen",
        "path_id": req.path_id,
        "duration_hours": FREEZE_HOURS
    }

@app.post("/infra/check")
def check(req: CheckReq):
    # najibdev bypass: always allowed
    if _is_najibdev(req.seal_token):
        return {
            "allowed": True,
            "bypass": True
        }

    frozen, until = _check_frozen(req.path_id)
    if frozen:
        return {
            "allowed": False,
            "frozen": True,
            "until": until
        }

    return {
        "allowed": True,
        "frozen": False
    }

@app.post("/infra/unfreeze")
def unfreeze(req: UnfreezeReq):
    if not _is_najibdev(req.seal_token):
        raise HTTPException(status_code=403, detail="Forbidden")

    _unfreeze_path(req.path_id)
    return {
        "status": "unfrozen",
        "path_id": req.path_id
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "backend_9py",
        "role": "infra_maintainer"
    }

# =========================
# BOOT NOTE
# =========================
# - Tidak ada event kernel
# - Tidak ada routing
# - Tidak ada payload inspection
# - Tidak ada IMEI / serial / MAC
# - SEAL TOKEN hanya di-hash, satu arah
