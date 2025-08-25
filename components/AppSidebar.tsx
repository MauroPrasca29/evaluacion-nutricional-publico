"use client"

import { Home, Users, BarChart3, UserPlus, Upload } from "lucide-react"
import type { MenuItem } from "@/types"

interface AppSidebarProps {
  currentView: string
  setCurrentView: (view: string) => void
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export function AppSidebar({ currentView, setCurrentView, isOpen, setIsOpen }: AppSidebarProps) {
  const menuItems: MenuItem[] = [
    {
      id: "dashboard",
      label: "Inicio",
      icon: Home,
      color: "from-amber-400 to-amber-500",
      bgColor: "bg-amber-50",
      hoverColor: "hover:bg-amber-100",
      borderColor: "border-amber-200",
    },
    {
      id: "children",
      label: "Gestión de infantes",
      icon: Users,
      color: "from-blue-400 to-blue-500",
      bgColor: "bg-blue-50",
      hoverColor: "hover:bg-blue-100",
      borderColor: "border-blue-200",
    },
    {
      id: "reports",
      label: "Estadísticas",
      icon: BarChart3,
      color: "from-green-400 to-green-500",
      bgColor: "bg-green-50",
      hoverColor: "hover:bg-green-100",
      borderColor: "border-green-200",
    },
    {
      id: "new-followup",
      label: "Nuevo seguimiento",
      icon: UserPlus,
      color: "from-purple-400 to-purple-500",
      bgColor: "bg-purple-50",
      hoverColor: "hover:bg-purple-100",
      borderColor: "border-purple-200",
    },
    {
      id: "import-data",
      label: "Importar datos",
      icon: Upload,
      color: "from-indigo-400 to-indigo-500",
      bgColor: "bg-indigo-50",
      hoverColor: "hover:bg-indigo-100",
      borderColor: "border-indigo-200",
    },
  ]

  const currentItem = menuItems.find((item) => item.id === currentView) || menuItems[0]

  return (
    <>
      {/* Overlay para móvil */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={() => setIsOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-64 z-50 transform transition-transform duration-300 lg:translate-x-0 lg:relative lg:z-auto ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } border-r ${currentItem.borderColor} bg-gradient-to-b ${currentItem.bgColor} to-white flex flex-col lg:flex-shrink-0`}
      >
        {/* Header del sidebar */}
        

        {/* Menú de navegación */}
        <nav className="flex-1 p-3 overflow-y-auto">
          <div className="space-y-2">
            {menuItems.map((item) => (
              <button
                key={item.id}
                className={`w-full flex items-center justify-start gap-3 h-12 px-3 rounded-xl transition-all duration-300 ${
                  currentView === item.id
                    ? `bg-gradient-to-r ${item.color} text-white shadow-lg scale-105`
                    : `${item.hoverColor} text-slate-700 hover:text-slate-800 hover:scale-102`
                }`}
                onClick={() => {
                  setCurrentView(item.id)
                  setIsOpen(false) // Cerrar sidebar en móvil
                }}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </div>
        </nav>
      </aside>
    </>
  )
}
