# ============================================================
# backend_4py.py
# CODE NAME: VISUAL CORTEX (UI/UX INTELLIGENCE)
# STATUS: ACTIVE - SERVING REACT CORE
# PORT: 8005
# ============================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
# Mengizinkan UI (HTML local atau server) untuk mengakses endpoint ini
CORS(app) 

# ============================================================
# LOGIC: HARDWARE TIER CLASSIFICATION
# ============================================================
def classify_tier(specs):
    """
    Menentukan kasta perangkat user:
    - GOD_TIER    : PC Gaming / Flagship Phone
    - MID_TIER    : Laptop Kantor / HP Menengah
    - POTATO_TIER : HP Lama / Chromebook
    """
    score = 0
    
    # 1. Analisis RAM (Memory)
    # Default ke 4GB jika browser tidak melapor
    ram = specs.get('memory', 4) 
    if ram >= 8:
        score += 3
    elif ram >= 4:
        score += 1
    
    # 2. Analisis CPU (Cores)
    cores = specs.get('cores', 4)
    if cores >= 6:
        score += 3
    elif cores >= 4:
        score += 1
        
    # 3. Analisis Layar (DPR - Retina/High DPI)
    dpr = specs.get('dpr', 1)
    if dpr > 2: # Layar sangat tajam butuh resource besar
        score -= 1 # Penalty untuk beban render

    # KEPUTUSAN FINAL
    if score >= 5:
        return "GOD_TIER"
    elif score >= 2:
        return "MID_TIER"
    else:
        return "POTATO_TIER"

# ============================================================
# ENDPOINT: UI POLICY
# ============================================================
@app.route('/ui/profile', methods=['POST'])
def get_ui_policy():
    """
    Menerima data hardware dari main.tsx, 
    Mengembalikan konfigurasi grafis yang optimal.
    """
    start_time = time.time()
    specs = request.json or {}
    
    print(f"🖥️ [VISUAL CORTEX] Analyzing Hardware: {specs}")
    
    tier = classify_tier(specs)
    policy = {}

    # KONFIGURASI BERDASARKAN TIER
    if tier == "GOD_TIER":
        policy = {
            "tier": "ULTRA",
            "quality": "ultra",      # CSS: --ui-quality: ultra
            "fps_cap": 120,          # CSS: --ui-fps: 120
            "animation_speed": 1.0,
            "effects": {
                "pseudo3D": True,    # DepthEngine ON
                "blur": True,        # Glassmorphism ON
                "particles": True,
                "shadows": "soft-dynamic"
            }
        }
    elif tier == "MID_TIER":
        policy = {
            "tier": "BALANCED",
            "quality": "medium",
            "fps_cap": 60,
            "animation_speed": 1.0,
            "effects": {
                "pseudo3D": True,    # DepthEngine Tetap ON (Ringan)
                "blur": False,       # Matikan blur (Berat di rendering)
                "particles": True,
                "shadows": "static"
            }
        }
    else: # POTATO_TIER
        policy = {
            "tier": "PERFORMANCE",
            "quality": "low",
            "fps_cap": 30,           # Hemat baterai/CPU
            "animation_speed": 0.5,  # Kurangi beban animasi
            "effects": {
                "pseudo3D": False,   # Matikan paralaks
                "blur": False,       # Matikan blur
                "particles": False,
                "shadows": "none"
            }
        }

    # Metadata respons
    response = {
        **policy,
        "meta": {
            "analysis_time": f"{(time.time() - start_time)*1000:.2f}ms",
            "detected_platform": specs.get('platform', 'unknown'),
            "engine_status": "OPTIMIZED"
        }
    }
    
    print(f"✨ [VISUAL CORTEX] Decision: {tier} -> {policy['quality']}")
    return jsonify(response)

@app.route('/', methods=['GET'])
def status():
    return jsonify({"status": "ONLINE", "service": "UI_INTELLIGENCE", "port": 8005})

# ============================================================
# BOOTSTRAP
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("👁️  VISUAL CORTEX (BACKEND 4) STARTED")
    print("👁️  LISTENING ON PORT 8005")
    print("👁️  READY TO OPTIMIZE UI RENDERING")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=8005)