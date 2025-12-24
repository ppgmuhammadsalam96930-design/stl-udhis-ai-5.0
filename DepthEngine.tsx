import { useEffect } from "react";

export function DepthEngine() {
  useEffect(() => {
    let running = true;
    let t = 0;

    function step() {
      if (!running) return;
      t += 0.002;

      const x = 50 + Math.sin(t) * 10;
      const y = 50 + Math.cos(t * 0.8) * 10;

      document.documentElement.style.setProperty("--px", `${x}%`);
      document.documentElement.style.setProperty("--py", `${y}%`);

      requestAnimationFrame(step);
    }

    step();

    document.addEventListener("visibilitychange", () => {
      running = !document.hidden;
      if (running) step();
    });

    return () => { running = false; };
  }, []);

  return null;
}
