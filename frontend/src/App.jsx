import { Suspense, lazy } from "react";
import "./index.css";

const Dashboard = lazy(() => import("./components/Dashboard"));

export default function App() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8", background: "#0a0e1a" }}>Loading NetGuardian…</div>}>
      <Dashboard />
    </Suspense>
  );
}
