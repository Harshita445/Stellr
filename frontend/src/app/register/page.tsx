"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export default function RegisterPage() {
  const router = useRouter();
  const [rollNumber, setRollNumber] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [sectionCode, setSectionCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          roll_number: rollNumber,
          display_name: displayName,
          section_code: sectionCode || undefined,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        const msg =
          body?.error?.message || body?.detail?.[0]?.msg || `Request failed (${res.status})`;
        throw new Error(msg);
      }
      const data = await res.json();
      localStorage.setItem("access_token", data.tokens.access_token);
      localStorage.setItem("refresh_token", data.tokens.refresh_token);
      localStorage.setItem("device_id", data.tokens.device_id);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-xl">✨</span>
              Join Stellr
            </div>
          </CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs text-text-muted block mb-1">
              Roll number
            </label>
            <input
              value={rollNumber}
              onChange={(e) => setRollNumber(e.target.value)}
              placeholder="e.g. 22CS001"
              required
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400 placeholder:text-text-muted/40"
            />
          </div>
          <div>
            <label className="text-xs text-text-muted block mb-1">
              Display name
            </label>
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Jane Doe"
              required
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400 placeholder:text-text-muted/40"
            />
          </div>
          <div>
            <label className="text-xs text-text-muted block mb-1">
              Section code
            </label>
            <input
              value={sectionCode}
              onChange={(e) => setSectionCode(e.target.value)}
              placeholder="e.g. CS-A"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400 placeholder:text-text-muted/40"
            />
          </div>
          {error && (
            <p className="text-sm text-red-400 text-center">{error}</p>
          )}
          <Button type="submit" variant="primary" className="w-full" disabled={loading}>
            {loading ? "Registering..." : "Register"}
          </Button>
          <p className="text-xs text-text-muted text-center">
            Already registered?{" "}
            <a
              href="/register"
              onClick={(e) => {
                e.preventDefault();
                const at = prompt("Paste your access token:");
                const did = prompt("Paste your device ID:");
                if (at && did) {
                  localStorage.setItem("access_token", at);
                  localStorage.setItem("device_id", did);
                  router.push("/dashboard");
                }
              }}
              className="text-accent-400 hover:text-accent-300"
            >
              Restore a previous session
            </a>
          </p>
        </form>
      </Card>
    </main>
  );
}
