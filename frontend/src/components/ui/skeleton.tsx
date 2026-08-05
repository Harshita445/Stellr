import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-gradient-to-r from-space-600/50 via-space-500/30 to-space-600/50 bg-[length:200%_100%] animate-shimmer",
        className,
      )}
    />
  );
}
