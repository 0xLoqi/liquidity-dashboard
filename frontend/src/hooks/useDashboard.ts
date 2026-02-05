"use client";

import useSWR from "swr";
import type { DashboardResponse } from "@/lib/types";
import { fetchDashboard } from "@/lib/api";

export function useDashboard() {
  const { data, error, isLoading, mutate } = useSWR<DashboardResponse>(
    "dashboard",
    fetchDashboard,
    {
      refreshInterval: 5 * 60 * 1000,
      revalidateOnFocus: true,
      dedupingInterval: 60 * 1000,
    }
  );

  return {
    dashboard: data,
    isLoading,
    isError: !!error,
    error,
    refresh: () => mutate(),
  };
}
