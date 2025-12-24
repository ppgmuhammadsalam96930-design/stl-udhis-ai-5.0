// hyperpool.cpp - The Sentinel Update
// Role: Watchdog & Sanitizer
#include <string>
#include <vector>
#include <emscripten.h>
#include <algorithm>

// Global State untuk memantau kesehatan sistem
static int panic_counter = 0;
static double last_action_time = 0.0;
static bool system_locked = false;

extern "C" {

// ==========================================
// 1. ROUTER CERDAS (Sesuai Backend Python)
// ==========================================
EMSCRIPTEN_KEEPALIVE
int route_intent(const char* text) {
    if (system_locked) return 999; // 999 = Sinyal Emergency/Locked
    if (!text) return 0;

    std::string t(text);
    
    // Normalisasi ke lowercase biar gak sensitif huruf besar/kecil
    std::transform(t.begin(), t.end(), t.begin(), ::tolower);

    // Deteksi Crash Loop (Jika user kirim "error" berulang kali)
    if (t.find("error") != std::string::npos || t.find("undefined") != std::string::npos) {
        panic_counter++;
        if (panic_counter > 5) {
            system_locked = true;
            return 999; // Trigger Mode Pemulihan
        }
    }

    // Update Routing Sesuai Python Backend
    if (t.find("vault") != std::string::npos) return 2; // Shadow Vault
    if (t.find("edu")   != std::string::npos) return 1; // Prometheus
    if (t.find("game")  != std::string::npos) return 4; // Visual Cortex
    if (t.find("infra") != std::string::npos) return 9; // Maintainer
    if (t.find("reset") != std::string::npos) {         // Manual Reset
        panic_counter = 0;
        system_locked = false;
        return 1;
    }

    // Reset panic counter jika input valid
    if (panic_counter > 0) panic_counter--; 
    
    return 1; // Default Safe Mode (Edu)
}

// ==========================================
// 2. INPUT SANITIZER (Pembersih Sampah)
// ==========================================
// Mencegah karakter aneh yang bikin HTML pecah/buggy
EMSCRIPTEN_KEEPALIVE
void sanitize_input(char* buffer, int length) {
    if (!buffer) return;
    int write_index = 0;
    for (int i = 0; i < length; i++) {
        char c = buffer[i];
        if (c == 0) break;
        
        // Hapus karakter kontrol aneh (kecuali newline) dan HTML tags berbahaya (< >)
        // Ini mencegah "Injection" yang bikin tampilan hancur.
        if ((c >= 32 && c <= 126) && c != '<' && c != '>') {
            buffer[write_index++] = c;
        }
    }
    buffer[write_index] = 0; // Null terminator baru
}

// ==========================================
// 3. STABILITY CHECK (Anti-Lag/Spam)
// ==========================================
EMSCRIPTEN_KEEPALIVE
int check_stability(double current_time) {
    // Jika request terlalu cepat (< 100ms), anggap spam/glitch
    if (current_time - last_action_time < 0.1) {
        return 0; // REJECT (Too fast)
    }
    last_action_time = current_time;
    
    if (system_locked) return -1; // SYSTEM DOWN
    
    return 1; // STABLE
}

// ==========================================
// 4. SCORING (Fitur Lama Tetap Ada)
// ==========================================
EMSCRIPTEN_KEEPALIVE
int fast_score(const char* text) {
    int score = 0;
    if (!text) return 0;
    std::string s(text);
    for (char c : s) {
        if (c >= 'A' && c <= 'Z') score++;
    }
    return score;
}

}
