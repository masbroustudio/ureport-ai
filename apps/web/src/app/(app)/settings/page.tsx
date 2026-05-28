"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { AVAILABLE_MODELS } from "@/components/chat/ChatComposer";

export default function SettingsPage() {
  const { user } = useAuth();
  const [defaultModel, setDefaultModel] = useState(AVAILABLE_MODELS[0].id);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("default_model");
    if (stored) setDefaultModel(stored);
  }, []);

  const handleSave = () => {
    localStorage.setItem("default_model", defaultModel);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Account</h2>
        <div className="space-y-2 text-sm">
          <div>
            <span className="text-muted-foreground">Name:</span>{" "}
            <span>{user?.name || "Not logged in"}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Email:</span>{" "}
            <span>{user?.email || "N/A"}</span>
          </div>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Default Model</h2>
        <select
          value={defaultModel}
          onChange={(e) => setDefaultModel(e.target.value)}
          className="w-full max-w-xs px-3 py-2 border border-border rounded-md bg-background text-foreground"
        >
          {AVAILABLE_MODELS.map((m) => (
            <option key={m.id} value={m.id}>
              {m.label}
            </option>
          ))}
        </select>
      </section>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Usage</h2>
        <p className="text-sm text-muted-foreground">
          Usage stats coming soon
        </p>
      </section>

      <Button onClick={handleSave}>
        {saved ? "Saved!" : "Save Settings"}
      </Button>
    </div>
  );
}
