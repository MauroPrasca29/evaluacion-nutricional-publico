"use client"

import { useState } from "react"
import { Bell, Menu, Settings, LogOut, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { NotificationPanel } from "./NotificationPanel"
import { UserProfile } from "./UserProfile"
import type { ThemeColors } from "@/types"

interface AppHeaderProps {
  theme: ThemeColors
  setSidebarOpen: (open: boolean) => void
}

export function AppHeader({ theme, setSidebarOpen }: AppHeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  return (
    <>
      <header
        className={`w-full border-b ${theme.headerBorder} bg-gradient-to-r ${theme.buttonColor} shadow-lg transition-all duration-500 relative z-10`}
      >
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden p-2 hover:bg-white/20 rounded-lg text-white"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-bold text-white">Evaluación Nutricional Infantil</h1>
              <p className="text-sm text-white/80">Sistema de seguimiento para comunidades vulnerables</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="relative hover:bg-white/20 rounded-lg text-white"
              onClick={() => setShowNotifications(true)}
            >
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-orange-500 rounded-full flex items-center justify-center">
                <span className="text-xs text-white font-bold">3</span>
              </span>
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="flex items-center gap-3 px-3 py-2 hover:bg-white/20 rounded-xl text-white"
                >
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-white/20 text-white font-bold text-sm">DR</AvatarFallback>
                  </Avatar>
                  <div className="text-left hidden sm:block">
                    <p className="text-sm font-bold text-white">Dra. Rosa Martínez</p>
                    <p className="text-xs text-white/80">Nutricionista</p>
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem className="hover:bg-amber-50 cursor-pointer" onClick={() => setShowProfile(true)}>
                  <Users className="w-4 h-4 mr-3" />
                  Mi Perfil
                </DropdownMenuItem>
                <DropdownMenuItem className="hover:bg-amber-50">
                  <Settings className="w-4 h-4 mr-3" />
                  Configuración
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-600 hover:bg-red-50">
                  <LogOut className="w-4 h-4 mr-3" />
                  Cerrar Sesión
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Panels */}
      <NotificationPanel isOpen={showNotifications} onClose={() => setShowNotifications(false)} />
      <UserProfile isOpen={showProfile} onClose={() => setShowProfile(false)} />
    </>
  )
}
