/**
 * OMNI-B : AUTH BLOCKING SHIELD
 * - Rate limit
 * - Short-lived signature cache
 * - Fail-safe reject
 */

const express = require('express');
const axios = require('axios');
const crypto = require('crypto');

const app = express();
app.use(express.json({ limit: '16kb' }));

// =====================
// CONFIG
// =====================
const AUTH_CORE = 'http://127.0.0.1:7000';
const LISTEN_PORT = 7001;

const RATE_LIMIT_WINDOW = 10_000; // 10 detik
const RATE_LIMIT_MAX = 20;        // max 20 req / window

const SIG_CACHE_TTL = 15_000;     // 15 detik

// =====================
// MEMORY STORES (RINGAN)
// =====================
const rateMap = new Map();   // ip -> { count, ts }
const sigCache = new Map();  // hash -> expireAt

// =====================
// HELPERS
// =====================
function now() {
  return Date.now();
}

function hashPayload(p) {
  return crypto.createHash('sha256')
    .update(JSON.stringify(p))
    .digest('hex');
}

// =====================
// RATE LIMIT
// =====================
function rateLimit(ip) {
  const entry = rateMap.get(ip);
  const t = now();

  if (!entry || t - entry.ts > RATE_LIMIT_WINDOW) {
    rateMap.set(ip, { count: 1, ts: t });
    return true;
  }

  if (entry.count >= RATE_LIMIT_MAX) {
    return false;
  }

  entry.count++;
  return true;
}

// =====================
// MAIN GATE
// =====================
app.post('/auth', async (req, res) => {
  const ip = req.ip || 'unknown';

  // 1️⃣ FAIL FAST — RATE LIMIT
  if (!rateLimit(ip)) {
    return res.status(429).end(); // silent drop
  }

  // 2️⃣ CACHE CHECK
  const sigHash = hashPayload(req.body);
  const cached = sigCache.get(sigHash);

  if (cached && cached > now()) {
    return res.json({ status: 'ok', cached: true });
  }

  // 3️⃣ FORWARD TO AUTH CORE
  try {
    const r = await axios.post(AUTH_CORE, req.body, {
      timeout: 2000
    });

    // cache only SUCCESS
    if (r.status === 200) {
      sigCache.set(sigHash, now() + SIG_CACHE_TTL);
    }

    return res.json({ status: 'ok' });

  } catch (e) {
    // FAIL-SAFE: DO NOT RETRY, DO NOT FORWARD
    return res.status(403).end();
  }
});

// =====================
// START
// =====================
app.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`🛡️ OMNI-B blocking AUTH on :${LISTEN_PORT}`);
});
