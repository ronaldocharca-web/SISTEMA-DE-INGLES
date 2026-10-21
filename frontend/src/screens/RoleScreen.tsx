"use client";

import { useState } from "react";

import { HistorialFlow } from "@/components/flows/HistorialFlow";
import { AdminDashboardScreen } from "@/screens/admin/AdminDashboardScreen";
import { AdminLoginScreen } from "@/screens/admin/AdminLoginScreen";

type Role = "student" | "admin-login" | "admin";

export function RoleScreen() {
  const [role, setRole] = useState<Role>("student");
  const [token, setToken] = useState("");
  if (role === "student") return <div className="student-entry"><button className="admin-icon" aria-label="Abrir acceso administrativo" title="Acceso administrativo" onClick={() => setRole("admin-login")}>♙</button><HistorialFlow /></div>;
  if (role === "admin-login") return <AdminLoginScreen onSuccess={(newToken) => { setToken(newToken); setRole("admin"); }} onBack={() => setRole("student")} />;
  return <AdminDashboardScreen token={token} onBack={() => { setToken(""); setRole("student"); }} />;
}
