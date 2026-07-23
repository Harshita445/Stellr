"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Users,
  Settings2,
  Trash2,
  LogOut,
  UserPlus,
  Loader2,
} from "lucide-react";
import { api, GroupDetail, GroupMember } from "@/lib/api-client";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function GroupDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [group, setGroup] = useState<GroupDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState("");
  const [addingMember, setAddingMember] = useState(false);
  const [memberInput, setMemberInput] = useState("");

  const loadGroup = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.groups.detail(id);
      setGroup(data);
      setNewName(data.name);
    } catch {
      router.push("/groups");
    } finally {
      setLoading(false);
    }
  }, [id, router]);

  useEffect(() => {
    loadGroup();
  }, [loadGroup]);

  const handleRename = async () => {
    if (!group || !newName.trim() || newName === group.name) return;
    setRenaming(true);
    try {
      const updated = await api.groups.rename(id, newName.trim());
      setGroup(updated);
    } catch {
      setNewName(group.name);
    } finally {
      setRenaming(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this constellation? This cannot be undone.")) return;
    try {
      await api.groups.delete(id);
      router.push("/groups");
    } catch {
      // handled
    }
  };

  const handleLeave = async () => {
    if (!confirm("Leave this constellation?")) return;
    try {
      await api.groups.removeMember(id, memberInput);
      router.push("/groups");
    } catch {
      // handled
    }
  };

  const handleAddMember = async () => {
    if (!memberInput.trim()) return;
    setAddingMember(true);
    try {
      const member = await api.groups.addMember(id, memberInput.trim());
      setGroup((prev) =>
        prev
          ? {
              ...prev,
              members: [...prev.members, member],
              member_count: prev.member_count + 1,
            }
          : prev,
      );
      setMemberInput("");
    } catch {
      // handled
    } finally {
      setAddingMember(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    const prev = group?.members || [];
    setGroup(
      (prevG) =>
        prevG && {
          ...prevG,
          members: prevG.members.filter((m) => m.user_id !== userId),
          member_count: prevG.member_count - 1,
        },
    );
    try {
      await api.groups.removeMember(id, userId);
    } catch {
      setGroup(
        (prevG) =>
          prevG && {
            ...prevG,
            members: prev,
            member_count: prev.length,
          },
      );
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 rounded-2xl" />
      </main>
    );
  }

  if (!group) return null;

  const currentUserId = memberInput;

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <a
          href="/groups"
          className="text-text-muted hover:text-text-primary transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </a>
        <div className="flex-1 min-w-0">
          <h1 className="text-2xl font-bold text-text-primary truncate">
            {group.name}
          </h1>
          <p className="text-sm text-text-muted mt-0.5">
            {group.member_count} {group.member_count === 1 ? "member" : "members"}
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Settings2 className="w-4 h-4 text-accent-400" />
              Settings
            </div>
          </CardTitle>
        </CardHeader>
        <div className="space-y-4">
          <div>
            <label className="text-xs text-text-muted block mb-1">Name</label>
            <div className="flex gap-2">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400"
              />
              <Button
                variant="primary"
                size="sm"
                disabled={renaming || !newName.trim() || newName === group.name}
                onClick={handleRename}
              >
                {renaming ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save"}
              </Button>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="danger" size="sm" onClick={handleDelete}>
              <Trash2 className="w-4 h-4" />
              Delete Constellation
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Members
            </div>
          </CardTitle>
        </CardHeader>
        <div className="space-y-2">
          {group.members.map((m) => (
            <div
              key={m.id}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors group"
            >
              <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 text-sm font-semibold shrink-0">
                {m.display_name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text-primary truncate">
                  {m.display_name}
                </p>
                {m.section_code && (
                  <p className="text-xs text-text-muted">{m.section_code}</p>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleRemoveMember(m.user_id)}
                className="opacity-0 group-hover:opacity-100"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-white/5">
          <label className="text-xs text-text-muted block mb-1">
            Add member by User ID
          </label>
          <div className="flex gap-2">
            <input
              value={memberInput}
              onChange={(e) => setMemberInput(e.target.value)}
              placeholder="User UUID..."
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary-400"
            />
            <Button
              variant="primary"
              size="sm"
              disabled={addingMember || !memberInput.trim()}
              onClick={handleAddMember}
            >
              {addingMember ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <UserPlus className="w-4 h-4" />
              )}
              Add
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-accent-400" />
              Availability
            </div>
          </CardTitle>
        </CardHeader>
        <div className="flex flex-col items-center gap-2 py-6 text-text-muted">
          <Users className="w-8 h-8 opacity-30" />
          <p className="text-sm">Coming in Phase 8</p>
          <p className="text-xs text-text-muted/60">
            Overlapping free periods will appear here
          </p>
        </div>
      </Card>
    </main>
  );
}
