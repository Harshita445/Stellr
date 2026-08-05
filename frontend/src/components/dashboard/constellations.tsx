"use client";

import { useState, useEffect, useCallback } from "react";
import { Users, Plus, ExternalLink, Sparkles, AlertCircle } from "lucide-react";
import { api, GroupSummary } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreateGroupDialog } from "@/components/groups/create-group-dialog";

export function Constellations() {
  const [groups, setGroups] = useState<GroupSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const loadGroups = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.groups.list();
      setGroups(data.groups);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Could not load your groups";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGroups();
  }, [loadGroups]);

  if (loading) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.03)_0%,transparent_60%)] pointer-events-none" />
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Your Groups
            </div>
          </CardTitle>
        </CardHeader>
        <p className="text-xs text-text-muted/70 -mt-3 mb-4 px-0">
          Compare schedules and find shared time
        </p>
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <Skeleton className="w-10 h-10 rounded-xl" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-16" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(239,68,68,0.03)_0%,transparent_60%)] pointer-events-none" />
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Your Groups
            </div>
          </CardTitle>
        </CardHeader>
        <p className="text-xs text-text-muted/70 -mt-3 mb-4 px-6">
          Compare schedules and find shared time
        </p>
        <div className="flex flex-col items-center gap-3 py-6 text-center">
          <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <p className="text-sm text-red-400">{error}</p>
          <Button variant="secondary" size="sm" onClick={loadGroups}>
            Try again
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.03)_0%,transparent_60%)] pointer-events-none" />
      <CardHeader>
        <CardTitle>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-accent-400" />
            Your Groups
            {groups.length > 0 && (
              <span className="text-xs font-normal text-text-muted ml-1">
                ({groups.length})
              </span>
            )}
          </div>
        </CardTitle>
        {groups.length > 0 && (
          <a
            href="/groups"
            className="text-text-muted hover:text-text-primary transition-colors"
            aria-label="View all groups"
          >
            <ExternalLink className="w-5 h-5" />
          </a>
        )}
      </CardHeader>
      <p className="text-xs text-text-muted/70 -mt-3 mb-4 px-6">
        Compare schedules and find shared time
      </p>

      {showCreate && (
        <CreateGroupDialog
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            loadGroups();
          }}
        />
      )}

      {groups.length === 0 ? (
        <div className="flex flex-col items-center gap-4 py-10 text-center relative">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-8 left-8 w-2 h-2 rounded-full bg-accent-400/15" />
            <div className="absolute bottom-12 right-8 w-1.5 h-1.5 rounded-full bg-primary-400/12" />
            <div className="absolute top-1/2 right-1/4 w-1 h-1 rounded-full bg-accent-400/8" />
            <div className="absolute bottom-1/3 left-1/3 w-1.5 h-1.5 rounded-full bg-primary-400/8" />
            <div className="absolute top-12 right-12 w-1 h-1 rounded-full bg-accent-300/6" />
            <div className="absolute bottom-8 left-1/4 w-1 h-1 rounded-full bg-primary-300/6" />
          </div>
          <div className="w-16 h-16 rounded-full bg-accent-500/8 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-accent-400/40" />
          </div>
          <div>
            <p className="text-base font-semibold text-text-primary">
              No groups yet
            </p>
            <p className="text-sm text-text-muted mt-1 max-w-xs">
              Create a group with your friends to find shared free time
            </p>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Button
              onClick={() => setShowCreate(true)}
              className="shadow-glow-sm hover:shadow-glow-md transition-shadow duration-200"
            >
              <Plus className="w-4 h-4" />
              Create Group
            </Button>
            <a
              href="/friends"
              className="text-xs text-accent-400 hover:text-accent-300 transition-colors"
            >
              or add a Star first
            </a>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {groups.slice(0, 3).map((g) => (
            <a key={g.id} href={`/groups/${g.id}`}>
              <div className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/[0.06] transition-colors cursor-pointer group">
                <div className="w-10 h-10 rounded-xl bg-accent-500/20 flex items-center justify-center text-accent-400 shrink-0">
                  <Users className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {g.name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {g.member_count} {g.member_count === 1 ? "member" : "members"}
                  </p>
                </div>
              </div>
            </a>
          ))}
          {groups.length > 3 && (
            <a
              href="/groups"
              className="block text-center text-xs text-accent-400 hover:text-accent-300 py-2 transition-colors"
            >
              View all {groups.length} groups
            </a>
          )}
        </div>
      )}
    </Card>
  );
}
