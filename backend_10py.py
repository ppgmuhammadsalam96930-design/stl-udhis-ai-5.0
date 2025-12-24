# backend_10py.py
# Behavioral Shadow Layer (Smooth Hook)
# Tidak blocking, tidak keras, tidak noisy

import time
import hashlib
from collections import deque, defaultdict
import ctypes
import time

sc = ctypes.CDLL("./libstealthcore.so")
sc.sc_jitter_ms.restype = ctypes.c_uint
sc.sc_entropy8.restype = ctypes.c_ubyte

# ==================== CONFIG ====================

WINDOW = 10.0          # detik observasi
MAX_EVENTS = 50        # per fingerprint
SOFT_LATENCY = 0.04    # 40ms (sengaja kecil & stabil)

# ==================== STATE ====================

event_pool = defaultdict(lambda: deque(maxlen=MAX_EVENTS))

# ==================== UTIL ====================

def fingerprint(request):
    """
    Fingerprint ringan & anonim
    Tidak pakai IP mentah
    """
    base = (
        request.headers.get("User-Agent", "")[:40] +
        request.headers.get("Accept-Language", "") +
        str(int(time.time() // WINDOW))
    )
    return hashlib.sha256(base.encode()).hexdigest()[:16]


def soft_sleep():
    """
    Latency halus, konsisten, tidak spike
    """
    time.sleep(SOFT_LATENCY)


# ==================== CORE HOOK ====================

def observe_and_influence(request, context):
    """
    Dipanggil oleh backend lain (opsional)
    context = dict bebas (intent, mode, dll)
    """
    fp = fingerprint(request)
    now = time.time()

    event_pool[fp].append(now)

    freq = len(event_pool[fp]) / WINDOW

    signal = {
        "behavior": "normal",
        "bias": "neutral",
        "note": None
    }
def stealth_touch():
    d = sc.sc_jitter_ms()
    if d:
        time.sleep(d / 1000)
    return sc.sc_entropy8()

    # ==================== BEHAVIOR ANALYSIS ====================

    if freq > 6:
        signal["behavior"] = "aggressive"
        signal["bias"] = "cooldown"
        signal["note"] = "high-frequency"

    elif freq > 3:
        signal["behavior"] = "fast-human"
        signal["bias"] = "soft"

    # ==================== CONTEXT REACTION ====================

    if context.get("mode") == "GHOST_ENCRYPTED":
        signal["bias"] = "silent"
        signal["note"] = "vault-path"

    # ==================== EFFECT (SMOOTH) ====================

    soft_sleep()

    return signal
