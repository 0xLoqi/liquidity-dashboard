"use client";

import useSWR from "swr";
import type { DashboardResponse } from "@/lib/types";
import { fetchDashboard } from "@/lib/api";

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
    }
  );

  return {
    dashboard: data,
    isLoading: isLoading || (isValidating && !data && !error),
    isError: !!error && !data,
    error,
    refresh: () => mutate(),
  };
}
