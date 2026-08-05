import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        "w-full bg-space-700/50 border border-space-400/30 rounded-lg px-4 py-2.5",
        "text-text-primary placeholder:text-text-muted/50",
        "focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/50",
        "transition-all duration-200",
        className,
      )}
      {...props}
    />
  );
}
