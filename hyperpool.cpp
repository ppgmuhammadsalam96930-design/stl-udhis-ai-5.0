// hyperpool.cpp
#include <string>
#include <emscripten.h>

extern "C" {

EMSCRIPTEN_KEEPALIVE
int route_intent(const char* text) {
    if (!text) return 0;
    std::string t(text);

    // Update sesuai backend Python yang ada:
    if (t.find("vault") != std::string::npos) return 2; // Ke backend_2py (Shadow Vault)
    if (t.find("edu")   != std::string::npos) return 1; // Ke backend_1py (Edu)
    if (t.find("game")  != std::string::npos) return 4; // Ke backend_4py (Visual)
    if (t.find("infra") != std::string::npos) return 9; // Ke backend_9py (Infra)

    return 1; // Default ke Edu
}

EMSCRIPTEN_KEEPALIVE
int fast_score(const char* text) {
    int score = 0;
    for (char c : std::string(text)) {
        if (c >= 'A' && c <= 'Z') score++;
    }
    return score;
}

}
