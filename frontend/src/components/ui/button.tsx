"use client";

import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md";
}

export function Button({
  className,
  variant = "primary",
  size = "md",
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200",
        "disabled:opacity-40 disabled:pointer-events-none",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-400",
        size === "sm" && "px-3 py-1.5 text-sm gap-1.5",
        size === "md" && "px-4 py-2 text-sm gap-2",
        variant === "primary" &&
          "bg-primary-600 text-white hover:bg-primary-500 active:bg-primary-700 shadow-glow-sm",
        variant === "secondary" &&
          "glass text-text-primary hover:bg-white/10 active:bg-white/15",
        variant === "ghost" &&
          "text-text-secondary hover:text-text-primary hover:bg-white/5",
        variant === "danger" &&
          "bg-red-600/20 text-red-400 hover:bg-red-600/30 border border-red-600/30",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
