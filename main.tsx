import { createRoot } from "react-dom/client";
import { DepthEngine } from "./DepthEngine";

// ===============================
// UI POLICY FETCHER
// ===============================
async function loadUIPolicy() {
  try {
    const payload = {
      width: window.innerWidth,
      height: window.innerHeight,
      dpr: window.devicePixelRatio || 1,
      memory: (navigator as any).deviceMemory || 2,
      cores: navigator.hardwareConcurrency || 2,
      platform: navigator.platform
    };

    const res = await fetch("http://localhost:8005/ui/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    return await res.json();
  } catch (e) {
    console.warn("[UI] backend_4py offline, fallback mode");
    return null;
  }
}

// ===============================
// APPLY UI POLICY → HTML
// ===============================
function applyPolicy(policy: any) {
  if (!policy) return;

  const root = document.documentElement;

  root.style.setProperty("--ui-quality", policy.quality);
  root.style.setProperty("--ui-fps", policy.fps_cap + "");

  if (policy.effects?.pseudo3D === false) {
    root.classList.add("ui-flat");
  }

  if (policy.effects?.blur === false) {
    root.classList.add("ui-no-blur");
  }
}

// ===============================
// BOOTSTRAP
// ===============================
(async function bootstrapUI() {
  const anchor = document.getElementById("ui-bg");
  if (!anchor) {
    console.warn("[UI] #ui-bg not found");
    return;
  }

  // 1. Mount visual engine
  createRoot(anchor).render(<DepthEngine />);

  // 2. Fetch UI policy
  const policy = await loadUIPolicy();
  applyPolicy(policy);

  console.log("🎨 UI Engine ready");
})();
