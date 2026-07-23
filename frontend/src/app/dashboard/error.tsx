"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Your Space</h1>
      </div>
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-center glass rounded-2xl p-5">
        <AlertTriangle className="w-10 h-10 text-red-400/70" />
        <div>
          <p className="text-text-primary font-medium">Could not load dashboard</p>
          <p className="text-sm text-text-muted mt-1">
            Something went wrong. Please try again.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={reset}>
          <RefreshCw className="w-4 h-4" />
          Try again
        </Button>
      </div>
    </main>
  );
}
