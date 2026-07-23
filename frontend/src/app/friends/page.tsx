"use client";

import { useState, useCallback } from "react";
import { ArrowLeft, Star } from "lucide-react";
import { api, FriendRelation } from "@/lib/api-client";
import { FriendSearch } from "@/components/friends/friend-search";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function FriendsPage() {
  const [friends, setFriends] = useState<FriendRelation[]>([]);

  const existingFriendIds = new Set(friends.map((f) => f.user.id));

  const handleAdd = useCallback(async (userId: string) => {
    const fallbackName = userId.slice(0, 8);
    const optimistic: FriendRelation = {
      id: `opt-${userId}`,
      user: { id: userId, display_name: fallbackName, section_code: null },
    };
    setFriends((prev) => [...prev, optimistic]);
    try {
      const result = await api.friends.add(userId);
      setFriends((prev) =>
        prev.map((f) =>
          f.id === optimistic.id
            ? {
                id: result.friendship_id,
                user: {
                  id: result.user.id,
                  display_name: result.user.display_name,
                  section_code: result.user.section_code,
                },
              }
            : f,
        ),
      );
    } catch {
      setFriends((prev) => prev.filter((f) => f.id !== `opt-${userId}`));
    }
  }, []);

  const handleRemove = useCallback(async (userId: string) => {
    const prev = [...friends];
    setFriends((f) => f.filter((fr) => fr.user.id !== userId));
    try {
      await api.friends.remove(userId);
    } catch {
      setFriends(prev);
    }
  }, [friends]);

  return (
    <main className="min-h-screen p-4 max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center gap-3">
        <a
          href="/dashboard"
          className="text-text-muted hover:text-text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400 rounded-lg"
          aria-label="Back to dashboard"
        >
          <ArrowLeft className="w-5 h-5" />
        </a>
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Stars</h1>
          <p className="text-sm text-text-muted mt-0.5">
            Find and connect with classmates
          </p>
        </div>
      </div>

      <FriendSearch
        existingFriendIds={existingFriendIds}
        onAdd={handleAdd}
        onRemove={handleRemove}
      />

      {friends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-accent-400" />
                Your Stars ({friends.length})
              </div>
            </CardTitle>
          </CardHeader>
          <div className="space-y-2">
            {friends.map((fr) => (
              <div
                key={fr.id}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 transition-colors group"
              >
                <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400 text-sm font-semibold shrink-0">
                  {fr.user.display_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">
                    {fr.user.display_name}
                  </p>
                  {fr.user.section_code && (
                    <p className="text-xs text-text-muted">
                      {fr.user.section_code}
                    </p>
                  )}
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleRemove(fr.user.id)}
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </main>
  );
}
