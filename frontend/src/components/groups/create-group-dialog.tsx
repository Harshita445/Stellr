"use client";

import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";

interface CreateGroupDialogProps {
  onClose: () => void;
  onCreated: () => void;
}

export function CreateGroupDialog({ onClose, onCreated }: CreateGroupDialogProps) {
  const [name, setName] = useState("");
  const [memberIds, setMemberIds] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    setError(null);
    try {
      const ids = memberIds
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      await api.groups.create(name.trim(), ids);
      onCreated();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create group";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="glass rounded-2xl p-6 w-full max-w-md space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">
            New Constellation
          </h2>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs text-text-muted block mb-1">
              Group name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Study Group"
              autoFocus
              maxLength={100}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400 placeholder:text-text-muted/40"
            />
          </div>

          <div>
            <label className="text-xs text-text-muted block mb-1">
              Member UUIDs <span className="opacity-50">(comma-separated, optional)</span>
            </label>
            <input
              value={memberIds}
              onChange={(e) => setMemberIds(e.target.value)}
              placeholder="uuid1, uuid2, ..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400 placeholder:text-text-muted/40"
            />
          </div>

          {error && (
            <p className="text-sm text-status-busy">{error}</p>
          )}

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              disabled={saving || !name.trim()}
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Create"
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
