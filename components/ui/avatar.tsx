import * as React from "react"
import { cn } from "@/lib/utils"

const Avatar = React.forwardRef<React.ElementRef<"div">, React.ComponentPropsWithoutRef<"div">>(
  ({ className, children, ...props }, ref) => (
    <div
      className={cn("relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full bg-muted", className)}
      ref={ref}
      {...props}
    >
      {children}
    </div>
  ),
)
Avatar.displayName = "Avatar"

const AvatarImage = React.forwardRef<React.ElementRef<"img">, React.ComponentPropsWithoutRef<"img">>(
  ({ className, ...props }, ref) => (
    <img className={cn("aspect-square h-full w-full object-cover", className)} ref={ref} {...props} />
  ),
)
AvatarImage.displayName = "AvatarImage"

const AvatarFallback = React.forwardRef<React.ElementRef<"span">, React.ComponentPropsWithoutRef<"span">>(
  ({ className, ...props }, ref) => (
    <span
      className={cn(
        "absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex h-full w-full items-center justify-center rounded-full bg-muted font-medium text-muted-foreground",
        className,
      )}
      ref={ref}
      {...props}
    />
  ),
)
AvatarFallback.displayName = "AvatarFallback"

const AvatarInitials = React.forwardRef<React.ElementRef<"span">, React.ComponentPropsWithoutRef<"span">>(
  ({ className, ...props }, ref) => (
    <span
      className={cn(
        "absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex h-full w-full items-center justify-center rounded-full font-medium text-muted-foreground",
        className,
      )}
      ref={ref}
      {...props}
    />
  ),
)
AvatarInitials.displayName = "AvatarInitials"

export { Avatar, AvatarImage, AvatarFallback, AvatarInitials }
