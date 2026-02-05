"use client";

import * as Switch from "@radix-ui/react-switch";
import type { DisplayMode } from "@/lib/types";

interface ModeToggleProps {
  mode: DisplayMode;
  onChange: (mode: DisplayMode) => void;
}

export function ModeToggle({ mode, onChange }: ModeToggleProps) {
  const isFinance = mode === "finance";

  return (
    <div className="flex items-center gap-3 boot-in" style={{ animationDelay: "0.55s" }}>
      <span
        className={`text-xs font-medium transition-colors ${
          !isFinance ? "text-foreground" : "text-muted/50"
        }`}
      >
        Plain English
      </span>
      <Switch.Root
        checked={isFinance}
        onCheckedChange={(checked) => onChange(checked ? "finance" : "plain")}
        className="relative w-10 h-5 rounded-full bg-surface-raised border border-border transition-colors data-[state=checked]:bg-accent/20 data-[state=checked]:border-accent/30"
      >
        <Switch.Thumb className="block w-4 h-4 rounded-full bg-muted transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px] data-[state=checked]:bg-accent" />
      </Switch.Root>
      <span
        className={`text-xs font-medium transition-colors ${
          isFinance ? "text-foreground" : "text-muted/50"
        }`}
      >
        Finance
      </span>
    </div>
  );
}
