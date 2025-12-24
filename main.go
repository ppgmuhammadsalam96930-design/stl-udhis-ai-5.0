package main

import (
	"bytes"
	"io"
	"log"
	"net/http"
	"time"
)

const (
	LISTEN_ADDR   = ":8080"
	PY_BACKEND    = "http://127.0.0.1"
	MAX_BODY_SIZE = 1 << 20 // 1MB
	TIMEOUT       = 5 * time.Second
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/edge/backend/", edgeHandler)

	server := &http.Server{
		Addr:         LISTEN_ADDR,
		Handler:      mux,
		ReadTimeout:  TIMEOUT,
		WriteTimeout: TIMEOUT,
	}

	log.Println("🟢 GO EDGE GUARD listening on", LISTEN_ADDR)
	log.Fatal(server.ListenAndServe())
}

func edgeHandler(w http.ResponseWriter, r *http.Request) {
	// 🔒 METHOD GUARD
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 🔒 SIZE GUARD
	r.Body = http.MaxBytesReader(w, r.Body, MAX_BODY_SIZE)
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Invalid body", http.StatusBadRequest)
		return
	}

	// 🔒 BASIC HEADER GUARD (opsional)
	if r.Header.Get("Content-Type") != "application/json" {
		http.Error(w, "Invalid content type", http.StatusUnsupportedMediaType)
		return
	}

	// 🎯 AMBIL INTENT DARI URL
	// contoh: /edge/backend/3
	intent := r.URL.Path[len("/edge/backend/"):]
	if intent == "" {
		http.Error(w, "Missing intent", http.StatusBadRequest)
		return
	}

	// 🚀 FORWARD KE PYTHON
	target := PY_BACKEND + ":800" + intent + "/api"

	req, err := http.NewRequest(http.MethodPost, target, bytes.NewReader(body))
	if err != nil {
		http.Error(w, "Upstream error", http.StatusBadGateway)
		return
	}

	req.Header = r.Header.Clone()

	client := &http.Client{Timeout: TIMEOUT}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Backend unreachable", http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// 🔁 RELAY RESPONSE
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}
