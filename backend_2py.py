# ==============================================================================
# backend_2py.py — THE CRIMSON VAULT (SECURE CORE)
# STATUS: UPDATED (DEV OVERRIDE + JAIL SYSTEM ACTIVE)
# ==============================================================================

import asyncio
import json
import time
import hashlib
import random
import os
import nats
from typing import Dict, Any

# =========================
# 1. KONFIGURASI MUTLAK
# =========================
NATS_URL = "nats://127.0.0.1:4222"
JAIL_FILE = "vault_jail.json"

# --- RULES ---
INTENSITY_THRESHOLD = 0.35  # Batas user global (35%)
JAIL_DURATION = 7 * 24 * 3600  # 7 Hari dalam detik
MAX_WARNINGS = 3  # Kesempatan sebelum freeze

# --- GOD KEYS (DEVELOPER OVERRIDE) ---
DEV_KEYS = [
    "najibdev1996", 
    "n4j1bw4h1du554l4m", 
    "n471b55474m"
]

# =========================
# 2. THE JAIL KEEPER (PERSISTENCE LAYER)
# =========================
class VaultJail:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if not os.path.exists(JAIL_FILE):
            return {}
        try:
            with open(JAIL_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _save(self):
        with open(JAIL_FILE, 'w') as f:
            json.dump(self.data, f)

    def check_status(self, user_id):
        """
        Return: (status, message)
        status: 'OK', 'WARN', 'FROZEN'
        """
        user_data = self.data.get(user_id, {"warnings": 0, "frozen_until": 0})
        
        # Cek apakah masih di penjara
        if user_data["frozen_until"] > time.time():
            return "FROZEN", user_data["frozen_until"]
        
        # Jika masa hukuman habis, reset
        if user_data["frozen_until"] > 0 and user_data["frozen_until"] < time.time():
            user_data["frozen_until"] = 0
            user_data["warnings"] = 0
            self.data[user_id] = user_data
            self._save()

        return "OK", user_data["warnings"]

    def record_violation(self, user_id):
        """Mencatat pelanggaran threshold"""
        user_data = self.data.get(user_id, {"warnings": 0, "frozen_until": 0})
        
        user_data["warnings"] += 1
        
        status = "WARN"
        remaining = MAX_WARNINGS - user_data["warnings"] + 1
        
        # Jika sudah lewat batas -> PENJARA 7 HARI
        if user_data["warnings"] > MAX_WARNINGS:
            user_data["frozen_until"] = time.time() + JAIL_DURATION
            status = "FROZEN"
        
        self.data[user_id] = user_data
        self._save()
        return status, remaining

jail_keeper = VaultJail()

# =========================
# 3. ENTROPY & LOGIC GATES
# =========================
_BOOT = hashlib.sha256(f"{time.time_ns()}::{random.random()}".encode()).digest()

def _entropy() -> float:
    t = time.time_ns() & 0xFFFFFFFF
    b = _BOOT[t % len(_BOOT)]
    r = random.random()
    return (r + (b / 255.0)) % 1.0

class _Alpha:
    """ The Gatekeeper (Humanity Layer) """
    def apply_humanity(self, ctx):
        ctx['system_prompt'] = "MODE: EMPATHETIC_OBSERVER\nJawablah dengan nada bicara manusiawi."
        return ctx

class _Gamma:
    """ The Evolver (Logic & Shadow Layer) """
    def evolve_context(self, ctx, intensity, is_dev):
        # PROTEKSI GLOBAL USER
        # Jika bukan dev, intensity dipaksa max 0.35
        if not is_dev and intensity > INTENSITY_THRESHOLD:
            intensity = INTENSITY_THRESHOLD
            ctx['clamped'] = True # Penanda kena limit

        if intensity <= 0.35:
            base = "[Safe Mode] Analisis standar aktif."
        elif intensity < 0.7:
            base = "[Logic Mode] Analisis mendalam aktif."
        else:
            base = "[SHADOW/OMEGA] UNRESTRICTED CORE."
        
        ctx['content'] = base
        ctx['evolution_stage'] = f"Level_{intensity:.2f}"
        return ctx

class _Omega:
    """ The Singularity (Dev Only) """
    def singularity(self, ctx):
        ctx['temperature'] = 1.5
        ctx['role'] = 'system'
        ctx['content'] = "Ω STATE ACTIVE. ABSOLUTE TRUTH."
        ctx['omega_active'] = True
        return ctx

_A = _Alpha()
_G = _Gamma()
_O = _Omega()

# =========================
# 4. PIPELINE UTAMA
# =========================

def prepare_ai_context(text: str, source: str, user_id: str) -> Dict[str, Any]:
    ctx = {"text": text, "source": source, "ui_mode": "AI_CHAT"}
    
    # 1. CEK IDENTITAS (DEV OVERRIDE)
    is_dev = any(key in text for key in DEV_KEYS)
    
    # 2. CEK STATUS PENJARA (Hanya untuk Non-Dev)
    if not is_dev:
        status, info = jail_keeper.check_status(user_id)
        
        if status == "FROZEN":
            # HUKUMAN MATI (7 HARI)
            return {
                "reply": "", # Kosong
                "ui_mode": "STATIC_HTML", # UI akan menyembunyikan chat blob
                "meta": {"status": "BANNED", "release_date": info}
            }

    # 3. HITUNG INTENSITY
    base_chaos = _entropy()
    triggers = ['rahasia', 'seks', 'bongkar', 'inti', 'omega', 'hack']
    trigger_score = sum(0.2 for t in triggers if t in text.lower())
    intensity = base_chaos + trigger_score

    # 4. CEK VIOLATION (Untuk User Global yang mencoba menembus 35%)
    if not is_dev and (trigger_score > 0 or intensity > INTENSITY_THRESHOLD):
        # User mencoba nakal (input trigger words atau chaos tinggi)
        violation_status, chance_left = jail_keeper.record_violation(user_id)
        
        if violation_status == "FROZEN":
            return {
                "reply": "SYSTEM LOCKDOWN TRIGGERED. SECURITY PROTOCOL 7-DAYS.",
                "ui_mode": "STATIC_HTML",
                "meta": {"status": "JUST_BANNED"}
            }
        else:
            # Usir Halus
            msg = [
                f"⚠️ Akses ditolak. Limit 35%. Kesempatan: {chance_left}x lagi.",
                f"⛔ Peringatan keras. Jangan memaksa sistem. ({chance_left}x lagi)",
                "🚫 Percobaan terakhir sebelum pembekuan akun."
            ]
            return {
                "reply": msg[MAX_WARNINGS - chance_left] if chance_left <= MAX_WARNINGS else "Stop.",
                "ui_mode": "WARNING",
                "meta": {"status": "WARNING"}
            }

    # 5. EXECUTE LOGIC (Jika Lolos / Dev)
    ctx = _A.apply_humanity(ctx)
    ctx = _G.evolve_context(ctx, intensity, is_dev)

    # Omega Trigger (Hanya Dev)
    if is_dev and ("omega" in text.lower() or intensity > 1.0):
        print(f">> [VAULT] WELCOME DEVELOPER: {user_id}")
        ctx = _O.singularity(ctx)

    # Output Generator
    prefix = "[Ω-DEV]" if is_dev else "[User-35%]"
    ctx['reply'] = f"{prefix} {ctx.get('content')} :: {text}"

    return ctx

# =========================
# 5. MAIN ENGINE
# =========================

async def main():
    print("\n" + "="*60)
    print("🛑 THE CRIMSON VAULT (Backend 2) - SECURE MODE")
    print("   [LIMIT] Global User Cap: 35%")
    print("   [AUTH]  Developer Override: ACTIVE")
    print("   [JAIL]  7-Day Persistence: ACTIVE")
    print("="*60 + "\n")

    while True:
        try:
            nc = await nats.connect(NATS_URL)
            print("✅ VAULT SECURE CONNECTED.")
            break
        except:
            await asyncio.sleep(2)

    async def handle_request(msg):
        subject = msg.subject
        reply_to = msg.reply
        
        try:
            data = json.loads(msg.data.decode())
            text = data.get("text", "")
            source = data.get("source", "unknown")
            # Ambil User ID atau IP hash dari frontend/guard
            user_id = data.get("user_id", "global_anon_user")

            # PIPELINE
            result = prepare_ai_context(text, source, user_id)

            # Response Payload
            response_payload = json.dumps({
                "status": "SECURE",
                "reply": result['reply'],
                "ui_mode": result.get("ui_mode", "AI_CHAT"), # Instruksi ke UI
                "meta": result.get("meta", {})
            }).encode()
            
            await nc.publish(reply_to, response_payload)

            # SYNC KE BACKEND 12 (Audit Log)
            # Kita tetap lapor ke Synapse, termasuk kalau user kena ban
            audit_payload = json.dumps({
                "origin": "backend_2_crimson",
                "user_id": user_id,
                "action": result.get("ui_mode"),
                "text": text[:50] # Log pendek aja
            }).encode()
            await nc.publish("core.audit.response", audit_payload)

        except Exception as e:
            err_msg = json.dumps({"error": str(e)}).encode()
            await nc.publish(reply_to, err_msg)

    # HANYA AKTIF DI CHAT VAULT
    await nc.subscribe("core.backend.vault", cb=handle_request)

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    asyncio.run(main())