"use client";

import { AlertTriangle, RefreshCw, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function GroupDetailError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <a href="/groups" className="text-text-muted hover:text-text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 rounded-lg" aria-label="Back to constellations">
          <ArrowLeft className="w-5 h-5" />
        </a>
        <h1 className="text-2xl font-bold text-text-primary">Constellation</h1>
      </div>
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-center glass rounded-2xl p-5">
        <AlertTriangle className="w-10 h-10 text-red-400/70" />
        <div>
          <p className="text-text-primary font-medium">Could not load constellation</p>
          <p className="text-sm text-text-muted mt-1">
            Something went wrong. Please try again.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" size="sm" onClick={reset}>
            <RefreshCw className="w-4 h-4" />
            Try again
          </Button>
          <a href="/groups">
            <Button variant="ghost" size="sm">
              Back to constellations
            </Button>
          </a>
        </div>
      </div>
    </main>
  );
}
