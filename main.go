package main

import (
	"io"
	"log"
	"net/http"
	"time"

	"github.com/nats-io/nats.go" // WAJIB: go get github.com/nats-io/nats.go
)

const (
	LISTEN_ADDR   = ":8080"
	NATS_URL      = nats.DefaultURL // Biasanya "nats://127.0.0.1:4222"
	MAX_BODY_SIZE = 1 << 20         // 1MB Security Cap
	TIMEOUT       = 5 * time.Second // Max waktu tunggu jawaban Python
)

// Global NATS Connection (Agar tidak connect ulang tiap request)
var nc *nats.Conn

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
	// =================================================
	// 🛡️ SECURITY LAYER (TIDAK DIUBAH - TETAP KERAS)
	// =================================================

	// 1. METHOD GUARD
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 2. SIZE GUARD (Anti-DDoS / Overflow)
	r.Body = http.MaxBytesReader(w, r.Body, MAX_BODY_SIZE)
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Invalid body or too large", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// 3. INTENT PARSING
	// URL: /edge/backend/3  --> intent: "3"
	// URL: /edge/backend/gov --> intent: "gov"
	intent := r.URL.Path[len("/edge/backend/"):]
	if intent == "" {
		http.Error(w, "Missing intent ID", http.StatusBadRequest)
		return
	}

	// =================================================
	// 🚀 TRANSPORT LAYER (UPGRADE KE NATS)
	// =================================================

	// Mapping Intent ke NATS Subject
	// Contoh: intent "3" -> subject "core.backend.3"
	// Contoh: intent "gov" -> subject "core.backend.gov"
	natsSubject := "core.backend." + intent

	// Kirim Request dan Tunggu Jawaban (Request-Reply Pattern)
	// Ini menggantikan http.Post yang lama. Jauh lebih ringan.
	msg, err := nc.Request(natsSubject, body, 4*time.Second)

	if err != nil {
		if err == nats.ErrNoResponders {
			// Artinya Python backend tujuannya mati/belum jalan
			log.Printf("⚠️  Service Offline: %s", natsSubject)
			http.Error(w, "Service Unavailable (Brain Offline)", http.StatusServiceUnavailable)
		} else if err == nats.ErrTimeout {
			// Artinya Python lambat mikir > 4 detik
			log.Printf("⏱️  Timeout waiting for: %s", natsSubject)
			http.Error(w, "Gateway Timeout (Brain Too Slow)", http.StatusGatewayTimeout)
		} else {
			// Error lain
			log.Printf("❌ NATS Error: %v", err)
			http.Error(w, "Internal Bus Error", http.StatusInternalServerError)
		}
		return
	}

	// =================================================
	// 📤 RESPONSE FORWARDING
	// =================================================

	// Set header JSON karena hampir semua backend kamu return JSON
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(msg.Data)
}