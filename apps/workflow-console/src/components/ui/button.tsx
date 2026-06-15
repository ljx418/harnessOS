import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils.js";

const buttonVariants = cva(
  "hos-workbench-focus inline-flex h-9 shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-md border text-sm font-semibold transition-colors disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border-primary bg-primary px-3 text-primary-foreground shadow-sm hover:bg-blue-700",
        secondary: "border-border bg-card px-3 text-foreground shadow-sm hover:bg-muted",
        ghost: "border-transparent bg-transparent px-2 text-muted-foreground hover:bg-muted hover:text-foreground",
        destructive: "border-red-200 bg-red-50 px-3 text-red-700 hover:bg-red-100",
        outline: "border-border bg-background px-3 text-foreground hover:bg-muted",
      },
      size: {
        default: "h-9",
        sm: "h-8 px-2.5 text-xs",
        icon: "h-9 w-9 p-0",
      },
    },
    defaultVariants: {
      variant: "secondary",
      size: "default",
    },
  },
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ asChild = false, className, size, variant, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ className, size, variant }))} ref={ref} {...props} />;
});

Button.displayName = "Button";

export { buttonVariants };
