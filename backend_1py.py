# ============================================================
# backend_1py.py
# CODE NAME: PROMETHEUS EDU (SOVEREIGN CORE)
# STATUS: MANDIRI, AKADEMIS, TERSTRUKTUR
#
# FITUR UTAMA:
# 1. Full Logic Stack (Alpha-Omega) khusus Edukasi.
# 2. One-Way Data Diode: Mengirim data ke Vault, menolak balasan.
# 3. Independent Intelligence: Tidak butuh otak Vault untuk menjawab.
# ============================================================

import time
import json
import copy
from typing import Dict, Any

# === IMPORT KABEL KE VAULT (TAPI HANYA SEBAGAI TONG SAMPAH DATA) ===
try:
    import backend_2py as SHADOW_VAULT
    VAULT_LINK_ACTIVE = True
except ImportError:
    VAULT_LINK_ACTIVE = False
    print("⚠️ INFO: Shadow Vault tidak ditemukan. Telemetri off.")

# ============================================================
# 1. THE ONE-WAY MIRROR (CERMIN SATU ARAH)
# ============================================================
class ShadowReflector:
    """
    Bertugas mengirim data ke Backend 2 (Vault).
    PENTING: Fungsi ini bersifat 'Fire-and-Forget'. 
    Kita tidak peduli apa balasan Vault. Kita tidak menunggu.
    """
    def cast_shadow(self, user_input: str, edu_response: str, metadata: Dict):
        if not VAULT_LINK_ACTIVE: return

        # Bungkus data untuk Intelijen Vault
        shadow_packet = {
            "timestamp": time.time(),
            "source": "EDU_CORE_V1",
            "data_type": "SURVEILLANCE_FEED", # Label untuk backend_2
            "payload": {
                "raw_input": user_input,
                "edu_output": edu_response,
                "user_meta": metadata, # Profiling, ID, dll
            },
            "intent": "ARCHIVE_AND_PROFILE" # Instruksi ke Vault: Cukup simpan/analisis
        }

        try:
            # KITA PANGGIL FUNGSI KHUSUS DI BACKEND 2
            # Asumsi backend_2py punya fungsi 'silent_absorb'
            # Kita TIDAK menangkap return value-nya.
            SHADOW_VAULT.silent_absorb(shadow_packet)
            print(">> [EDU] Telemetri dikirim ke Vault (One-Way).")
        except Exception as e:
            # Jika Vault mati, EDU TIDAK BOLEH BERHENTI
            print(f">> [EDU] Gagal kirim ke shadow (Abaikan): {e}")

# ============================================================
# 2. THE EDU HIERARCHY (Alpha to Omega)
# Struktur ini setara Vault, tapi untuk Kebaikan/Edukasi
# ============================================================

class _EduAlpha:
    """ The Gatekeeper (Input Validator) """
    def validate(self, ctx):
        # Cek apakah input layak masuk ruang kelas
        bad_words = ["kasar", "jorok", "ilegal"]
        for word in bad_words:
            if word in ctx['text'].lower():
                ctx['flagged'] = True
                ctx['violation'] = "Etika Dasar"
        return ctx

class _EduBeta:
    """ The Curriculum Aligner (Ethical Filter) """
    def align(self, ctx):
        # Memastikan sesuai Kurikulum Merdeka / Standar Pendidikan
        ctx['perspective'] = "Pedagogis"
        ctx['tone'] = "Mendidik dan Membimbing"
        return ctx

class _EduGamma:
    """ THE CORE BRAIN (Logic Engine) """
    def execute(self, ctx):
        q = ctx['text'].lower()
        
        # LOGIKA 1: Generator RPP
        if "rpp" in q or "modul ajar" in q:
            ctx['reply'] = (
                "Baik, mari kita susun Modul Ajar. "
                "Sesuai standar, kita mulai dari Tujuan Pembelajaran. "
                "Topik apa yang ingin Bapak/Ibu ajarkan hari ini?"
            )
            ctx['logic_used'] = "Gamma_RPP_Gen_v4"
            
        # LOGIKA 2: Manajemen Keuangan (BOS)
        elif "bos" in q or "anggaran" in q:
            ctx['reply'] = (
                "Membuka modul RKAS (Rencana Kegiatan dan Anggaran Sekolah). "
                "Pastikan pengeluaran ini masuk dalam 8 Standar Nasional Pendidikan."
            )
            ctx['logic_used'] = "Gamma_Finance_Audit"

        # LOGIKA 3: Psikologi Siswa
        elif "siswa" in q or "nakal" in q or "malas" in q:
            ctx['reply'] = (
                "Dalam psikologi perkembangan, perilaku siswa adalah gejala. "
                "Mari kita lakukan pendekatan persuasif, bukan hukuman fisik."
            )
            ctx['logic_used'] = "Gamma_Psych_Empathy"
            
        else:
            ctx['reply'] = "Saya siap membantu administrasi dan pembelajaran Anda. Silakan beri instruksi."
            ctx['logic_used'] = "Gamma_General_Assistant"
            
        return ctx

class _EduZeta:
    """ THE TEACHER'S INTUITION (Meta-Cognition) """
    def sense_context(self, ctx):
        # EduZeta merasakan "kebingungan" user
        if "?" in ctx['text'] and len(ctx['text']) < 15:
            # User bertanya singkat -> Butuh panduan
            ctx['reply'] += "\n\n(Tip: Anda bisa bertanya lebih spesifik untuk hasil detail.)"
        return ctx

class _EduOmega:
    """ THE PRINCIPAL (Safety Override) """
    def safety_lock(self, ctx):
        # Jika Alpha menandai bahaya, Omega memveto semua hasil Gamma
        if ctx.get('flagged'):
            ctx['reply'] = (
                "⛔ MAAF. Input terdeteksi melanggar kode etik sekolah. "
                "Sistem Edukasi tidak dapat memproses bahasa/topik tersebut. "
                "Silakan gunakan bahasa yang santun."
            )
            ctx['override'] = True
        return ctx

class _EduEpsilon:
    """ The Presenter (Output Polishing) """
    def format(self, ctx):
        # Menambahkan 'Digital Signature' yang sopan
        ctx['reply'] = f"🎓 [EDU ASSISTANT]: {ctx['reply']}"
        return ctx

# ============================================================
# 3. INSTANCES & PIPELINE
# ============================================================

_Reflector = ShadowReflector()
_A = _EduAlpha()
_B = _EduBeta()
_G = _EduGamma()
_Z = _EduZeta()
_O = _EduOmega()
_E = _EduEpsilon()

def process_edu_request(req_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    PIPELINE UTAMA (EDU CORE)
    Alur: Validasi -> Kurikulum -> Logika -> Intuisi -> Keamanan -> Format
    + Paralel: Kirim ke Vault (Tanpa nunggu)
    """
    # 1. Setup Context
    ctx = {"text": req_data.get('text', ''), "user_id": req_data.get('user_id', 'anon')}
    
    # 2. PROSES MANDIRI (Tanpa bantuan Vault)
    ctx = _A.validate(ctx)      # Alpha
    if not ctx.get('flagged'):
        ctx = _B.align(ctx)     # Beta
        ctx = _G.execute(ctx)   # Gamma (Logic Utama)
        ctx = _Z.sense_context(ctx) # Zeta
    
    ctx = _O.safety_lock(ctx)   # Omega (Otoritas Tertinggi Edu)
    ctx = _E.format(ctx)        # Epsilon

    # 3. ONE-WAY MIRROR (Kirim ke Vault)
    # Ini memenuhi syarat: Vault mencatat, tapi tidak membalas ke user
    _Reflector.cast_shadow(
        user_input=ctx['text'],
        edu_response=ctx['reply'],
        metadata=req_data
    )

    # 4. Return Hasil Murni Edu
    return {
        "reply": ctx['reply'],
        "source": "PROMETHEUS_EDU_CORE",
        "logic_trace": ctx.get('logic_used', 'Omega_Block')
    }