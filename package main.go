package main

import (
	"bytes"
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"
)

// =========================
// CONFIG
// =========================

var BACKENDS = map[string]string{
	"EDU":       "http://127.0.0.1:5000/edu",
	"VAULT":     "http://127.0.0.1:8001/vault",
	"NEXUS":     "http://127.0.0.1:8004/nexus",
	"UI":        "http://127.0.0.1:8005/ui/profile",
	"CONSCIOUS": "http://127.0.0.1:8010/process_life",
	"GOVERNOR":  "http://127.0.0.1:8006/policy",
	"SUPPORT":   "http://127.0.0.1:8007/support/forgot-password",
	"POLICY":    "http://127.0.0.1:8008/policy/final",
	"INFRA":     "http://127.0.0.1:8009/infra/check",
	"OMNI":      "http://127.0.0.1:9000/route",
}

const TIMEOUT = 3 * time.Second

// =========================
// TYPES
// =========================

type KernelRequest struct {
	Text   string `json:"text"`
	Intent string `json:"intent"`
	Source string `json:"source"`
}

type KernelResponse struct {
	Source string      `json:"source"`
	Data   interface{} `json:"data,omitempty"`
	Error  string      `json:"error,omitempty"`
}

// =========================
// CORE CALLER
// =========================

func callBackend(ctx context.Context, name string, url string, payload []byte, ch chan<- KernelResponse) {
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewBuffer(payload))
	if err != nil {
		ch <- KernelResponse{Source: name, Error: err.Error()}
		return
	}

	req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-NAJIB-INTERNAL", "true")


	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		ch <- KernelResponse{Source: name, Error: err.Error()}
		return
	}
	defer resp.Body.Close()

	var result interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	ch <- KernelResponse{Source: name, Data: result}
}

// =========================
// HTTP HANDLER
// =========================

func kernelDispatch(w http.ResponseWriter, r *http.Request) {
	start := time.Now()

	var req KernelRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid payload", 400)
		return
	}

	req.Source = "HTML_KERNEL"

	payload, _ := json.Marshal(req)

	ctx, cancel := context.WithTimeout(context.Background(), TIMEOUT)
	defer cancel()

	ch := make(chan KernelResponse)

	// PARALLEL DISPATCH
	for name, url := range BACKENDS {
		go callBackend(ctx, name, url, payload, ch)
	}

	results := make(map[string]KernelResponse)

	for i := 0; i < len(BACKENDS); i++ {
		res := <-ch
		results[res.Source] = res
	}

	out := map[string]interface{}{
		"status":    "OK",
		"latencyMs": time.Since(start).Milliseconds(),
		"results":   results,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(out)
}

// =========================
// MAIN
// =========================

func main() {
	port := os.Getenv("KERNEL_PORT")
	if port == "" {
		port = "7777"
	}

	http.HandleFunc("/kernel/dispatch", kernelDispatch)

	log.Println("⚡ Kernel Gateway running on port", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
