"use client";

import { useState, useEffect } from "react";
import { User, Copy, Check, Sparkles } from "lucide-react";
import { api, UserProfile } from "@/lib/api-client";
import { Card } from "@/components/ui/card";

export function ProfileCard() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api.users.me()
      .then(setProfile)
      .catch(() => {});
  }, []);

  if (!profile) return null;

  const handleCopyCode = async () => {
    if (!profile.stellr_code) return;
    try {
      await navigator.clipboard.writeText(profile.stellr_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_right,rgba(139,92,246,0.06)_0%,transparent_70%)] pointer-events-none" />
      <div className="relative z-10 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-500/15 flex items-center justify-center shrink-0">
            <User className="w-5 h-5 text-primary-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-text-primary truncate">
              {profile.display_name}
            </p>
            {profile.section_code && (
              <p className="text-xs text-text-muted">{profile.section_code}</p>
            )}
          </div>
        </div>

        {profile.stellr_code && (
          <div className="space-y-1.5">
            <p className="text-[11px] text-text-muted uppercase tracking-wider">
              Your Stellr Code
            </p>
            <button
              onClick={handleCopyCode}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-space-700/60 border border-space-400/20 hover:border-primary-500/30 transition-colors group"
            >
              <Sparkles className="w-3.5 h-3.5 text-primary-400/60 shrink-0" />
              <code className="text-sm font-mono text-text-primary tracking-wider flex-1 text-left">
                {profile.stellr_code}
              </code>
              {copied ? (
                <Check className="w-3.5 h-3.5 text-status-available shrink-0" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-text-muted group-hover:text-primary-400 transition-colors shrink-0" />
              )}
            </button>
            <p className="text-[10px] text-text-muted/60">
              Share this code so others can add you
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
