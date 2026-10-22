"use client";

import { useState } from "react";

import { HistorialFlow } from "@/components/flows/HistorialFlow";
import { AdminDashboardScreen } from "@/screens/admin/AdminDashboardScreen";
import { AdminLoginScreen } from "@/screens/admin/AdminLoginScreen";

type Role = "student" | "admin-login" | "admin";

export function RoleScreen() {
  const [role, setRole] = useState<Role>("student");
  const [token, setToken] = useState("");

  if (role === "student") {
    return (
      <div className="student-entry">
        <button
          className="admin-icon"
          aria-label="Abrir acceso administrativo"
          title="Panel administrativo"
          onClick={() => setRole("admin-login")}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <span>Admin</span>
        </button>
        <HistorialFlow />
      </div>
    );
  }

  if (role === "admin-login") {
    return (
      <AdminLoginScreen
        onSuccess={(newToken) => {
          setToken(newToken);
          setRole("admin");
        }}
        onBack={() => setRole("student")}
      />
    );
  }

  return (
    <AdminDashboardScreen
      token={token}
      onBack={() => {
        setToken("");
        setRole("student");
      }}
    />
  );
}
