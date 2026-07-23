"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api, AvailabilityResponse } from "@/lib/api-client";

interface UseAvailabilityPollingOptions {
  intervalMs?: number;
  enabled?: boolean;
}

interface UseAvailabilityPollingResult {
  data: AvailabilityResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useGroupAvailabilityPolling(
  groupId: string | null,
  options: UseAvailabilityPollingOptions = {},
): UseAvailabilityPollingResult {
  const { intervalMs = 30000, enabled = true } = options;
  const [data, setData] = useState<AvailabilityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.availability.compareGroup(groupId);
      setData(result);
    } catch {
      setError("Failed to load availability");
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    if (!groupId || !enabled) return;

    refresh();

    intervalRef.current = setInterval(refresh, intervalMs);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [groupId, enabled, intervalMs, refresh]);

  return { data, loading, error, refresh };
}

export function useFriendAvailabilityPolling(
  friendId: string | null,
  options: UseAvailabilityPollingOptions = {},
): UseAvailabilityPollingResult {
  const { intervalMs = 30000, enabled = true } = options;
  const [data, setData] = useState<AvailabilityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    if (!friendId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await api.availability.compareFriend(friendId);
      setData(result);
    } catch {
      setError("Failed to load availability");
    } finally {
      setLoading(false);
    }
  }, [friendId]);

  useEffect(() => {
    if (!friendId || !enabled) return;

    refresh();

    intervalRef.current = setInterval(refresh, intervalMs);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [friendId, enabled, intervalMs, refresh]);

  return { data, loading, error, refresh };
}
