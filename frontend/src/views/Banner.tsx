import React from "react";
import { Info } from "lucide-react";

export const Banner: React.FC = () => (
  <div style={{ background: "linear-gradient(90deg, #1e1b4b, #0f172a)", borderBottom: "1px solid rgba(99, 102, 241, 0.2)", padding: "0.5rem 1rem", fontSize: "0.8rem", color: "#c7d2fe", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}>
    <Info size={14} color="#818cf8" />
    <span><strong>Scientific Disclosure:</strong> Retrospective research on 2019-2023 Glasgow SCOOT data. Not a live operations system or dynamic commuter tracker.</span>
  </div>
);
