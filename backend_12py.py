# ==============================================================================
# backend_12py.py — THE SYNAPSE ORACLE (CACHE & ANOMALY SENTINEL)
# ROLE:
# 1. Semantic Caching (Mencegah backend mikir 2x untuk hal sama)
# 2. Dead Man Switch (Membangunkan Governor jika mati)
# 3. NATS Traffic Analyzer (Mendeteksi Semantic Spam)
# ==============================================================================

import asyncio
import json
import time
import hashlib
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoRespondersError

# =========================
# KONFIGURASI SINAPSIS
# =========================
NATS_URL = "nats://127.0.0.1:4222"
CACHE_TTL = 300  # 5 Menit memori jangka pendek
MAX_REPEATS = 4  # Batas toleransi spam semantik

# Memori Volatile (RAM Cepat)
# Format: {hash_pertanyaan: {response: str, timestamp: float}}
SEMANTIC_CACHE = {} 

# Counter Spam Semantik
# Format: {user_fingerprint: count}
TRAFFIC_HEATMAP = {}

# Status Governor
GOVERNOR_LAST_SEEN = time.time()

async def main():
    print("\n" + "="*60)
    print("🔮 THE SYNAPSE ORACLE (Backend 12) IS ONLINE")
    print("   [LISTENING]  Monitor NATS Traffic")
    print("   [CACHING]    Semantic Deduplication Active")
    print("   [GUARDING]   Watching The Watchmen")
    print("="*60 + "\n")

    # 1. KONEKSI KE JANTUNG NATS
    nc = await nats.connect(NATS_URL)

    # =====================================================
    # FUNGSI 1: SEMANTIC CACHE INTERCEPTOR
    # Mencegat pertanyaan sebelum Backend berat (1py/3py/5py) mikir
    # =====================================================
    async def intercept_request(msg):
        subject = msg.subject
        reply_to = msg.reply
        
        try:
            data = json.loads(msg.data.decode())
            text = data.get("text", "").strip().lower()
            
            # Buat Hash dari pertanyaan (Simpel & Cepat)
            req_hash = hashlib.md5(f"{subject}:{text}".encode()).hexdigest()
            
            # CEK CACHE
            if req_hash in SEMANTIC_CACHE:
                entry = SEMANTIC_CACHE[req_hash]
                # Jika cache masih valid (< 5 menit)
                if time.time() - entry["timestamp"] < CACHE_TTL:
                    print(f"⚡ [CACHE HIT] Melayani instan: {text[:30]}...")
                    # Balas langsung ke main.go, bypass backend berat!
                    response_payload = json.dumps(entry["response"]).encode()
                    await nc.publish(reply_to, response_payload)
                    return # Selesai, backend lain tidak perlu kerja

        except Exception as e:
            pass # Jangan bikin crash kalau JSON rusak

        # Kalau tidak ada di cache, biarkan backend asli yang jawab
        # Kita tidak melakukan apa-apa, NATS akan meneruskan ke Subscriber asli (Queue Group)

    # =====================================================
    # FUNGSI 2: RESPONSE RECORDER (Untuk isi Cache)
    # Mendengarkan jawaban backend lain untuk disimpan
    # =====================================================
    async def record_response(msg):
        # Ini agak tricky di NATS request-reply standar.
        # Strategi: Kita subscribe ke channel khusus "core.audit.>"
        # Backend lain nanti disarankan publish copy jawaban ke sini.
        pass 

    # =====================================================
    # FUNGSI 3: DEAD MAN SWITCH (Watchdog)
    # Memastikan Governor (Backend 6) masih hidup
    # =====================================================
    async def watchdog_loop():
        global GOVERNOR_LAST_SEEN
        while True:
            try:
                # Ping Governor lewat NATS
                response = await nc.request("core.backend.governor", b'{"ping":true}', timeout=1)
                GOVERNOR_LAST_SEEN = time.time()
                # print("💚 Governor Alive")
# =========================
# META-REASONING LAYER
# =========================

def estimate_depth(text: str) -> int:
    """
    Estimasi kedalaman pertanyaan (ringan & cepat)
    """
    score = 0
    if len(text) > 120:
        score += 3
    if any(k in text for k in ["mengapa", "bagaimana", "arsitektur", "implikasi", "konsekuensi"]):
        score += 3
    if any(k in text for k in ["contoh", "langkah", "detail"]):
        score += 2
    return score

def decide_mode(intent: str, depth: int) -> str:
    """
    Menentukan MODE BERPIKIR AI
    """
    if depth > 7 and intent == "vault":
        return "reflective_lore"
    elif intent == "edu":
        return "structured_teaching"
    else:
        return "direct_response"
            except:
                print("Lr [ALERT] GOVERNOR (BACKEND 6) SILENT/DEAD!")
                # Aksi Darurat: Auto-restart script atau kirim sinyal ke guard.exe
                # Di sini kita broadcast pesan darurat ke UI
                alert_msg = json.dumps({
                    "type": "SYSTEM_ALERT",
                    "msg": "GOVERNOR DOWN. RUNNING UNGOVERNED."
                }).encode()
                await nc.publish("ui.alert", alert_msg)
            
            await asyncio.sleep(5)

    # =====================================================
    # SUBSCRIPTIONS
    # =====================================================
    
    # 1. Intercept Traffic Masuk (Wildcard)
    # Kita pakai Queue Group yang beda supaya tidak mencuri pesan, tapi mengintip
    # Tapi untuk Cache, kita harus lebih cepat dari backend.
    # NATS architecture note: Untuk cache pre-emption yang sempurna, 
    # idealnya ini jadi 'Frontman'. Tapi untuk 'Soft' approach,
    # kita biarkan dia pasif dulu atau perlu modifikasi main.go sedikit lagi.
    
    # Untuk sekarang, kita buat dia sebagai "Shadow Logger" dan "Governor Watcher"
    await nc.subscribe("core.backend.>", cb=intercept_request)

    # Jalankan Watchdog di background
    asyncio.create_task(watchdog_loop())

    # Keep Alive
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Synapse Offline.")
