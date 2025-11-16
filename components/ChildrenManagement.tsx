"use client"

import { useState, useEffect } from "react"
import { Search, Plus, Eye, Loader2 } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { NewChildForm } from "./NewChildForm"
import { apiFetch } from "@/lib/api"
import { ChildProfile } from "./ChildProfile"
import type { ThemeColors, NewChildForm as NewChildFormType, Child } from "@/types"

interface ChildrenManagementProps {
  theme: ThemeColors
}

interface Infante {
  id_infante: number
  nombre: string
  fecha_nacimiento: string
  genero: string
  sede_id: number | null
  acudiente_id: number | null
}

export function ChildrenManagement({ theme }: ChildrenManagementProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedChild, setSelectedChild] = useState<Child | null>(null)
  const [showNewChildForm, setShowNewChildForm] = useState(false)
  const [children, setChildren] = useState<Infante[]>([])
  const [loading, setLoading] = useState(true)

  // Cargar infantes desde la API
  useEffect(() => {
    fetchChildren()
  }, [])

  const fetchChildren = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
      const response = await apiFetch(`${apiBase}/api/children/`)
      
      if (response.ok) {
        const data = await response.json()
        setChildren(data)
      } else {
        console.error("Error al cargar infantes")
      }
    } catch (error) {
      console.error("Error de conexión al cargar infantes:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredChildren = children.filter((child) =>
    child.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleNewChild = () => {
    setShowNewChildForm(true)
  }

  const handleSaveChild = (childData: NewChildFormType) => {
    console.log("Nuevo niño registrado:", childData)
    // Recargar la lista de infantes después de guardar
    fetchChildren()
    setShowNewChildForm(false)
  }

  const handleSelectChild = (child: Infante) => {
    // Convertir Infante a Child para mantener compatibilidad con ChildProfile
    const childData: Child = {
      id: child.id_infante.toString(),
      name: child.nombre,
      age: calculateAge(child.fecha_nacimiento),
      gender: child.genero === "M" ? "Masculino" : "Femenino",
      birthDate: child.fecha_nacimiento,
      community: child.sede_id ? child.sede_id.toString() : "N/A",
      guardian: child.acudiente_id ? child.acudiente_id.toString() : "N/A",
      phone: "N/A",
      address: "N/A",
      status: "N/A",
      lastCheckup: "N/A",
      weight: 0,
      height: 0,
      bmi: 0,
    }
    setSelectedChild(childData)
  }

  const calculateAge = (birthDate: string): string => {
    const birth = new Date(birthDate)
    const today = new Date()
    const years = today.getFullYear() - birth.getFullYear()
    const months = today.getMonth() - birth.getMonth()
    
    if (years > 0) {
      return `${years} año${years !== 1 ? 's' : ''}`
    } else {
      return `${months} mes${months !== 1 ? 'es' : ''}`
    }
  }

  const getInitials = (nombre: string): string => {
    return nombre
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
      .toUpperCase()
  }

  if (showNewChildForm) {
    return <NewChildForm theme={theme} onClose={() => setShowNewChildForm(false)} onSave={handleSaveChild} />
  }

  if (selectedChild) {
    return <ChildProfile child={selectedChild} theme={theme} onBack={() => setSelectedChild(null)} />
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Gestión de Infantes</h1>
        <p className="text-lg text-slate-600">
          Administra y consulta la información de los niños registrados en el sistema
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
          <Input
            placeholder="Buscar por nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 border-amber-200 focus:border-amber-400"
          />
        </div>
        <Button
          onClick={handleNewChild}
          className={`bg-gradient-to-r ${theme.buttonColor} text-white transition-all duration-300 hover:scale-105`}
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuevo Niño
        </Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
          <span className="ml-3 text-slate-600">Cargando infantes...</span>
        </div>
      ) : filteredChildren.length === 0 ? (
        <Card className={`${theme.cardBorder} bg-gradient-to-r ${theme.cardBg}`}>
          <CardContent className="p-12 text-center">
            <p className="text-slate-600 text-lg">
              {searchTerm
                ? "No se encontraron infantes con ese nombre"
                : "No hay infantes registrados. Haz clic en 'Nuevo Niño' para agregar uno."}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredChildren.map((child) => (
            <Card
              key={child.id_infante}
              className={`${theme.cardBorder} bg-gradient-to-r ${theme.cardBg} hover:shadow-lg transition-shadow duration-300 hover:scale-102 cursor-pointer`}
              onClick={() => handleSelectChild(child)}
            >
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <Avatar className="w-12 h-12">
                      <AvatarFallback
                        className={`bg-gradient-to-br ${theme.buttonColor.split(" ")[0]} text-white font-bold`}
                      >
                        {getInitials(child.nombre)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-slate-800">{child.nombre}</h3>
                      <p className="text-sm text-slate-600">
                        {calculateAge(child.fecha_nacimiento)} • {child.genero === "M" ? "Masculino" : "Femenino"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleSelectChild(child)
                      }}
                      className={`${theme.cardBorder} hover:bg-amber-50 transition-colors`}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      Ver Perfil
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && filteredChildren.length > 0 && (
        <div className="text-center text-sm text-slate-600">
          Mostrando {filteredChildren.length} de {children.length} infante{children.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  )
}