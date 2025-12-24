// vault_guard.rs
// wasm-pack build --target web

use wasm_bindgen::prelude::*;
use chacha20poly1305::aead::{Aead, KeyInit};
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce};
use rand::RngCore;

const SECRET_GHOST_KEY: &[u8; 32] = b"NAJIBDEV_SUPER_SECRET_KEY_v99_XY";

#[wasm_bindgen]
pub struct VaultSentinel {
    integrity_locked: bool,
}

#[wasm_bindgen]
impl VaultSentinel {

    #[wasm_bindgen(constructor)]
    pub fn new() -> VaultSentinel {
        VaultSentinel { integrity_locked: true }
    }

    /* ==================== DECRYPT (FROM PYTHON) ==================== */
    pub fn unlock_data(&self, encrypted_hex: &str, nonce_hex: &str) -> String {
        if !self.integrity_locked {
            return "ACCESS_DENIED".to_string();
        }

        let key = Key::from_slice(SECRET_GHOST_KEY);
        let cipher = ChaCha20Poly1305::new(key);

        let nonce_bytes = match hex::decode(nonce_hex) {
            Ok(v) if v.len() == 12 => v,
            _ => return "ERROR: INVALID_NONCE".to_string()
        };

        let ciphertext = match hex::decode(encrypted_hex) {
            Ok(v) => v,
            Err(_) => return "ERROR: INVALID_PAYLOAD".to_string()
        };

        let nonce = Nonce::from_slice(&nonce_bytes);

        match cipher.decrypt(nonce, ciphertext.as_ref()) {
            Ok(plaintext) => String::from_utf8_lossy(&plaintext).to_string(),
            Err(_) => "ERROR: DECRYPT_FAIL".to_string()
        }
    }

    /* ==================== ENCRYPT (TO PYTHON) ==================== */
    pub fn seal_packet(&self, text: &str) -> JsValue {
        let key = Key::from_slice(SECRET_GHOST_KEY);
        let cipher = ChaCha20Poly1305::new(key);

        // ✅ NONCE UNIK PER REQUEST (MINIMAL FIX)
        let mut nonce_bytes = [0u8; 12];
        rand::thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        match cipher.encrypt(nonce, text.as_bytes()) {
            Ok(ciphertext) => {
                // ⬅️ FORMAT NYAMBUNG DENGAN backend_2py KAMU
                JsValue::from_serde(&serde_json::json!({
                    "payload": hex::encode(ciphertext),
                    "nonce": hex::encode(nonce_bytes),
                    "mode": "GHOST_ENCRYPTED"
                })).unwrap()
            }
            Err(_) => JsValue::from_str("ERROR")
        }
    }
}
