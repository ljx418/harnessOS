import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "../../lib/utils.js";

export const Tabs = TabsPrimitive.Root;

export const TabsList = React.forwardRef<React.ElementRef<typeof TabsPrimitive.List>, React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>>(
  ({ className, ...props }, ref) => <TabsPrimitive.List className={cn("inline-flex h-9 items-center rounded-lg bg-muted p-1", className)} ref={ref} {...props} />,
);
TabsList.displayName = TabsPrimitive.List.displayName;

export const TabsTrigger = React.forwardRef<React.ElementRef<typeof TabsPrimitive.Trigger>, React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>>(
  ({ className, ...props }, ref) => (
    <TabsPrimitive.Trigger
      className={cn(
        "hos-workbench-focus inline-flex h-7 items-center justify-center rounded-md px-3 text-xs font-semibold text-muted-foreground transition-colors data-[state=active]:bg-card data-[state=active]:text-primary data-[state=active]:shadow-sm",
        className,
      )}
      ref={ref}
      {...props}
    />
  ),
);
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName;

export const TabsContent = TabsPrimitive.Content;
