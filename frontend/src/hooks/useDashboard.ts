"use client";

import { useEffect } from "react";
import useSWR from "swr";
import type { DashboardResponse } from "@/lib/types";
import { fetchDashboard } from "@/lib/api";

const CACHE_KEY = "flowstate_dashboard_cache_v1";

function readCache(): DashboardResponse | undefined {
  if (typeof window === "undefined") return undefined;
  try {
    const raw = window.localStorage.getItem(CACHE_KEY);
    return raw ? (JSON.parse(raw) as DashboardResponse) : undefined;
  } catch {
    return undefined;
  }
}

function writeCache(data: DashboardResponse) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(CACHE_KEY, JSON.stringify(data));
  } catch {
    // Quota exceeded or storage disabled — ignore.
  }
}

export function useDashboard() {
  const { data, error, isLoading, isValidating, mutate } = useSWR<DashboardResponse>(
    "dashboard",
    fetchDashboard,
    {
      refreshInterval: 5 * 60 * 1000,
      revalidateOnFocus: true,
      dedupingInterval: 60 * 1000,
      // Cold-starts on the free Render tier can take ~30s. Retry quietly so
      // the user sees a single "loading" state instead of a flicker into
      // "error" and back. ~10 retries × 4s ≈ 40s total budget.
      errorRetryCount: 10,
      errorRetryInterval: 4000,
      shouldRetryOnError: true,
      fallbackData: typeof window === "undefined" ? undefined : readCache(),
    }
  );

  useEffect(() => {
    if (data) writeCache(data);
  }, [data]);

  return {
    dashboard: data,
    isLoading: isLoading && !data,
    isRefreshing: isValidating && !!data,
    isError: !!error && !data,
    error,
    refresh: () => mutate(),
  };
}
