"use client"

import { useState } from "react"
import { Search, Plus, Eye } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { NewChildForm } from "./NewChildForm"
import { ChildProfile } from "./ChildProfile"
import type { ThemeColors, NewChildForm as NewChildFormType } from "@/types"
import { mockChildren } from "@/data/mockData"

interface ChildrenManagementProps {
  theme: ThemeColors
}

export function ChildrenManagement({ theme }: ChildrenManagementProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedChild, setSelectedChild] = useState<number | null>(null)
  const [showNewChildForm, setShowNewChildForm] = useState(false)

  const filteredChildren = mockChildren.filter(
    (child) =>
      child.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      child.community.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const handleNewChild = () => {
    setShowNewChildForm(true)
  }

  const handleSaveChild = (childData: NewChildFormType) => {
    console.log("Nuevo niño registrado:", childData)
    // Aquí se guardaría en la base de datos
    alert("Niño registrado exitosamente")
  }

  if (showNewChildForm) {
    return <NewChildForm theme={theme} onClose={() => setShowNewChildForm(false)} onSave={handleSaveChild} />
  }

  if (selectedChild) {
    const child = mockChildren.find((c) => c.id === selectedChild)
    if (child) {
      return <ChildProfile child={child} theme={theme} onBack={() => setSelectedChild(null)} />
    }
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
            placeholder="Buscar por nombre o comunidad..."
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

      <div className="grid gap-4">
        {filteredChildren.map((child) => (
          <Card
            key={child.id}
            className={`${theme.cardBorder} bg-gradient-to-r ${theme.cardBg} hover:shadow-lg transition-shadow duration-300 hover:scale-102`}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback
                      className={`bg-gradient-to-br ${theme.buttonColor.split(" ")[0]} text-white font-bold`}
                    >
                      {child.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{child.name}</h3>
                    <p className="text-slate-600">
                      {child.age} • {child.community}
                    </p>
                    <p className="text-sm text-slate-500">
                      Última visita: {child.lastVisit} • Peso: {child.weight} kg
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge
                    className={`${
                      child.status === "normal" ? "bg-green-100 text-green-800" : "bg-orange-100 text-orange-800"
                    }`}
                  >
                    {child.status}
                  </Badge>
                  <Button
                    variant="outline"
                    className={`${theme.cardBorder} hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
                    onClick={() => setSelectedChild(child.id)}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Ver perfil
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
