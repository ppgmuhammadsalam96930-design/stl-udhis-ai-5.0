package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"io"
	"log"
	"net"
	"net/http"
	"time"

	"github.com/nats-io/nats.go"
)

const (
	LISTEN_ADDR   = ":8080"
	NATS_URL      = nats.DefaultURL // Biasanya "nats://127.0.0.1:4222"
	MAX_BODY_SIZE = 1 << 20         // 1MB Security Cap
	TIMEOUT       = 5 * time.Second // Max waktu tunggu jawaban Python
)

// Global NATS Connection (Agar tidak connect ulang tiap request)
var nc *nats.Conn
func generateUserID(r *http.Request) string {
	// Ambil IP user (realistis & konsisten)
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		ip = r.RemoteAddr
	}

	// Optional: tambahkan User-Agent agar lebih stabil
	ua := r.UserAgent()

	// Salt statis (boleh diganti, JANGAN dipublish)
	seed := ip + "|" + ua + "|CRIMSON_VAULT_SALT"

	hash := sha256.Sum256([]byte(seed))
	return hex.EncodeToString(hash[:])
}

func main() {
	var err error

	// 1. INISIALISASI NATS (Jantung Baru)
	// Kita gunakan opsi retry agar kalau NATS belum nyala, dia coba terus
	opts := []nats.Option{
		nats.Name("GO-EDGE-GUARD"),
		nats.ReconnectWait(2 * time.Second),
		nats.MaxReconnects(-1), // Unlimited reconnects
	}

	log.Println("⚡ Menghubungkan ke NATS Backbone...")
	nc, err = nats.Connect(NATS_URL, opts...)
	if err != nil {
		log.Fatal("❌ Gagal connect ke NATS: ", err)
	}
	defer nc.Close()
	log.Println("✅ TERHUBUNG KE NATS. Sistem Syaraf Aktif.")

	// 2. SERVER HTTP (Wajah Lama, Mesin Baru)
	mux := http.NewServeMux()
	mux.HandleFunc("/edge/backend/", edgeHandler)

	server := &http.Server{
		Addr:         LISTEN_ADDR,
		Handler:      mux,
		ReadTimeout:  TIMEOUT,
		WriteTimeout: TIMEOUT,
	}

	log.Println("🛡️  GO EDGE GUARD listening on", LISTEN_ADDR)
	log.Fatal(server.ListenAndServe())
}

func edgeHandler(w http.ResponseWriter, r *http.Request) {
	// METHOD GUARD
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// SIZE GUARD
	r.Body = http.MaxBytesReader(w, r.Body, MAX_BODY_SIZE)
	rawBody, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Invalid body or too large", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Parse JSON
	var payload map[string]interface{}
	if err := json.Unmarshal(rawBody, &payload); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Inject user_id (CRITICAL)
	payload["user_id"] = generateUserID(r)

	// Default source (kalau frontend tidak kirim)
	if _, ok := payload["source"]; !ok {
		payload["source"] = "vault"
	}

	// Encode ulang
	body, _ := json.Marshal(payload)

	// INTENT PARSING
	intent := r.URL.Path[len("/edge/backend/"):]
	if intent == "" {
		http.Error(w, "Missing intent ID", http.StatusBadRequest)
		return
	}

	natsSubject := "core.backend." + intent

	// REQUEST ke NATS
	msg, err := nc.Request(natsSubject, body, 4*time.Second)
	if err != nil {
		if err == nats.ErrNoResponders {
			http.Error(w, "Service Unavailable", http.StatusServiceUnavailable)
		} else if err == nats.ErrTimeout {
			http.Error(w, "Gateway Timeout", http.StatusGatewayTimeout)
		} else {
			http.Error(w, "Internal Bus Error", http.StatusInternalServerError)
		}
		return
	}

	// RESPONSE
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(msg.Data)
}