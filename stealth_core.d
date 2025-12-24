// stealth_core.d
// Compile:
// dmd -O -release -betterC -fPIC -shared stealth_core.d -of=libstealthcore.so

extern(C):

// ==================== INTERNAL STATE ====================

__gshared ulong seed = 0;
__gshared ulong pulseCounter = 0;

// ==================== UTIL ====================

ulong mix(ulong x) {
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    return x * 2685821657736338717UL;
}

ulong nowNano() {
    import core.time : MonoTime;
    return MonoTime.currTime.ticks;
}

// ==================== PUBLIC API ====================

// 1️⃣ JITTER MICRO (0–6 ms)
// Dipakai untuk timing noise
uint sc_jitter_ms() {
    if (seed == 0) {
        seed = mix(nowNano());
    }
    seed = mix(seed + nowNano());
    return cast(uint)(seed % 7); // 0–6 ms
}

// 2️⃣ ENTROPY KECIL (0–255)
// Dipakai sebagai sinyal mikro
ubyte sc_entropy8() {
    seed = mix(seed + pulseCounter);
    return cast(ubyte)(seed & 0xFF);
}

// 3️⃣ PULSE STATE
// Dipanggil berkala untuk mutasi internal
void sc_pulse() {
    pulseCounter++;
    seed = mix(seed ^ nowNano());
}

// 4️⃣ HEALTH CHECK (OPTIONAL)
// Bukan security signal
uint sc_health() {
    return cast(uint)((seed ^ pulseCounter) & 0xFFFF);
}
