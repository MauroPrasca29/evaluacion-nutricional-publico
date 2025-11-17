"use client"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { AppSidebar } from "@/components/AppSidebar"
import { AppHeader } from "@/components/AppHeader"
import { Dashboard } from "@/components/Dashboard"
import { ChildrenManagement } from "@/components/ChildrenManagement"
import { NewFollowUpForm } from "@/components/NewFollowUpForm"
import { NewChildForm } from "@/components/NewChildForm"
import { ImportData } from "@/components/ImportData"
import { AdvancedStatistics } from "@/components/AdvancedStatistics"
import { UsersManagement } from "@/components/UsersManagement"
import { getThemeColors } from "@/utils/theme"
import type { NewChildForm as NewChildFormType } from "@/types"

export default function NutritionalAssessmentApp() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [currentView, setCurrentView] = useState("dashboard")
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showNewChildForm, setShowNewChildForm] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)

  // Evitar problemas de hidratación
  useEffect(() => {
    setMounted(true)
    // Verificar si hay token y obtener rol del usuario
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    // Obtener datos del usuario para saber si es admin
    fetch("/api/auth-me", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => {
        setIsAdmin(data.es_admin || false)
      })
      .catch(err => {
        console.error("Error fetching user data:", err)
      })
  }, [router])

  const theme = getThemeColors(currentView)

  const handleNewChild = () => {
    setShowNewChildForm(true)
  }

  const handleSaveChild = (childData: NewChildFormType) => {
    console.log("Nuevo niño registrado:", childData)
    alert("Niño registrado exitosamente")
    setShowNewChildForm(false)
  }

  const handleNavigate = (view: string) => {
    setCurrentView(view)
    setShowNewChildForm(false)
  }

  const renderContent = () => {
    if (showNewChildForm) {
      return <NewChildForm theme={theme} onClose={() => setShowNewChildForm(false)} onSave={handleSaveChild} />
    }

    switch (currentView) {
      case "children":
        return <ChildrenManagement theme={theme} />
      case "reports":
        return <AdvancedStatistics theme={theme} />
      case "new-followup":
        return <NewFollowUpForm theme={theme} />
      case "import-data":
        return <ImportData theme={theme} />
      case "users":
        return <UsersManagement theme={theme} />
      default:
        return <Dashboard theme={theme} onNewChild={handleNewChild} onNavigate={handleNavigate} />
    }
  }

  // No renderizar nada hasta que el componente esté montado en el cliente
  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-lg text-gray-600">Cargando...</div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br ${theme.gradient} transition-all duration-700`}>
      {/* Header que ocupa todo el ancho */}
      <AppHeader theme={theme} setSidebarOpen={setSidebarOpen} />

      {/* Contenido principal debajo del header */}
      <div className="flex">
        {/* Sidebar */}
        <AppSidebar
          currentView={currentView}
          setCurrentView={setCurrentView}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
          isAdmin={isAdmin}
        />

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto">{renderContent()}</div>
        </main>
      </div>
    </div>
  )
}
