"use client";

import { useState, useEffect, useCallback } from "react";
import { Users, Plus, ExternalLink } from "lucide-react";
import { api, GroupSummary } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreateGroupDialog } from "@/components/groups/create-group-dialog";

export function Constellations() {
  const [groups, setGroups] = useState<GroupSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const loadGroups = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.groups.list();
      setGroups(data.groups);
    } catch {
      // handled
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGroups();
  }, [loadGroups]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Constellations
            </div>
          </CardTitle>
        </CardHeader>
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-accent-400" />
            Constellations
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
          >
            <ExternalLink className="w-5 h-5" />
          </a>
        )}
      </CardHeader>

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
        <div className="flex flex-col items-center gap-2 py-6 text-text-muted">
          <Users className="w-8 h-8 opacity-30" />
          <p className="text-sm">No constellations yet</p>
          <p className="text-xs text-text-muted/60">
            Create a group to compare schedules
          </p>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4" />
            Create
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          {groups.slice(0, 3).map((g) => (
            <a key={g.id} href={`/groups/${g.id}`}>
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
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
              className="block text-center text-xs text-accent-400 hover:text-accent-300 py-2"
            >
              View all {groups.length} constellations
            </a>
          )}
        </div>
      )}
    </Card>
  );
}
