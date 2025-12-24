# backend_11py.py
# AI Broker: EDU (Demo) + VAULT (Developer)

import requests
from collections import defaultdict

# ================= API KEYS =================

# 🔹 DEMO KEY (USER EDU)
DEMO_AI_KEY = "2a355b7c123c40e7a2491c783754c599.3JlgmJzVp9I-mC2rECpPlwmA"

# 🔹 DEVELOPER KEY (KAMU SENDIRI)
# (boleh sama, boleh beda — ini ladang dev)
DEV_AI_KEY = "2a355b7c123c40e7a2491c783754c599.3JlgmJzVp9I-mC2rECpPlwmA"

# ================= LIMIT CONFIG =================

EDU_LIGHT_MAX = 6   # jawaban kritis / analitis
EDU_HEAVY_MAX = 3   # proses besar (modul ajar, silabus)

edu_light = defaultdict(int)
edu_heavy = defaultdict(int)

# ================= PESAN SOPAN =================

EDU_EXHAUSTED = (
    "Maaf, sesi kreasi perangkat ajar demo telah selesai 🙏\n\n"
    "Silakan melakukan registrasi manual dengan API key Anda sendiri "
    "dengan batas 100 penggunaan per hari.\n\n"
    "Untuk akses maksimal dan tanpa batasan, "
    "Anda dapat melakukan pembelian resmi melalui pihak developer.\n\n"
    "Terima kasih atas pengertiannya."
)

VAULT_GREETING = (
    "Hai, senang kamu sudah kembali 🌱\n"
    "Crimson Vault siap menemani eksplorasi idemu."
)

# ================= CORE =================

def call_ai(
    mode,
    user_text,
    session_id="default",
    is_heavy=False
):
    """
    mode:
      - 'edu'   -> user umum (demo)
      - 'vault' -> developer (kamu)
    """

    # ===== VAULT MODE (DEV BEBAS) =====
    if mode == "vault":
        return _call_provider(
            api_key=DEV_AI_KEY,
            system_prompt=VAULT_GREETING,
            user_text=user_text,
            max_tokens=700
        )

    # ===== EDU MODE (DEMO TERBATAS) =====
    if mode == "edu":
        if is_heavy:
            if edu_heavy[session_id] >= EDU_HEAVY_MAX:
                return EDU_EXHAUSTED
            edu_heavy[session_id] += 1
            max_tokens = 450
        else:
            if edu_light[session_id] >= EDU_LIGHT_MAX:
                return EDU_EXHAUSTED
            edu_light[session_id] += 1
            max_tokens = 250

        system_prompt = (
            "Anda adalah AI Edu dengan kemampuan analisis mendalam. "
            "Jawab runtut, kritis, dan membantu pembelajaran."
        )

        return _call_provider(
            api_key=DEMO_AI_KEY,
            system_prompt=system_prompt,
            user_text=user_text,
            max_tokens=max_tokens
        )

    return "Mode AI tidak dikenali."

# ================= PROVIDER =================

def _call_provider(api_key, system_prompt, user_text, max_tokens):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    try:
        r = requests.post(
            "https://api.demo-ai-provider.com/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=15
        )
        return (
            r.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    except Exception:
        return "AI sedang tidak tersedia, silakan coba kembali."
