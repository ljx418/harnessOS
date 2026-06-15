import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils.js";

const badgeVariants = cva("inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-semibold", {
  variants: {
    variant: {
      default: "border-blue-200 bg-blue-50 text-blue-700",
      secondary: "border-border bg-muted text-muted-foreground",
      success: "border-emerald-200 bg-emerald-50 text-emerald-700",
      warning: "border-amber-200 bg-amber-50 text-amber-800",
      destructive: "border-red-200 bg-red-50 text-red-700",
      violet: "border-violet-200 bg-violet-50 text-violet-700",
    },
  },
  defaultVariants: {
    variant: "secondary",
  },
});

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ className, variant }))} {...props} />;
}
