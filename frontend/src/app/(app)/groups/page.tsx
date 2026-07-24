"use client";

import { useState, useEffect, useCallback } from "react";
import { ArrowLeft, Users, Plus, ExternalLink } from "lucide-react";
import { api, GroupSummary } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreateGroupDialog } from "@/components/groups/create-group-dialog";

export default function GroupsPage() {
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

  const handleCreated = () => {
    setShowCreate(false);
    loadGroups();
  };

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <a
            href="/dashboard"
            className="text-text-muted hover:text-text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 rounded-lg"
            aria-label="Back to dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </a>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Your Groups</h1>
            <p className="text-sm text-text-muted mt-0.5">
              Your groups and teams
            </p>
          </div>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4" />
          New
        </Button>
      </div>

      {showCreate && (
        <CreateGroupDialog
          onClose={() => setShowCreate(false)}
          onCreated={handleCreated}
        />
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2].map((i) => (
            <Card key={i}>
              <div className="flex items-center gap-3">
                <Skeleton className="w-12 h-12 rounded-xl" />
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-5 w-40" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : groups.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-2 py-8 text-text-muted">
            <Users className="w-10 h-10 opacity-30" />
            <p className="text-sm">No groups yet</p>
            <p className="text-xs text-text-muted/60">
              Create a group to start comparing availability
            </p>
            <Button onClick={() => setShowCreate(true)}>
              <Plus className="w-4 h-4" />
              Create Group
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-3">
          {groups.map((g) => (
            <a key={g.id} href={`/groups/${g.id}`}>
              <Card className="hover:bg-white/[0.08] transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-accent-500/20 flex items-center justify-center text-accent-400 shrink-0">
                    <Users className="w-6 h-6" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-medium text-text-primary truncate">
                      {g.name}
                    </p>
                    <p className="text-xs text-text-muted">
                      {g.member_count} {g.member_count === 1 ? "member" : "members"}
                    </p>
                  </div>
                  <ExternalLink className="w-4 h-4 text-text-muted/40" />
                </div>
              </Card>
            </a>
          ))}
        </div>
      )}
    </main>
  );
}
