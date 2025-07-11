"use client"

import type React from "react"

import { useState } from "react"
import { Save, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { ThemeColors } from "@/types"

interface NewChildFormProps {
  theme: ThemeColors
  onClose: () => void
  onSave: (childData: any) => void
}

export function NewChildForm({ theme, onClose, onSave }: NewChildFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    birthDate: "",
    gender: "",
    guardian: "",
    phone: "",
    address: "",
    community: "",
    weight: "",
    height: "",
    observations: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
    onClose()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 mb-2">Registrar Nuevo Niño</h1>
          <p className="text-slate-600">Ingresa la información del nuevo niño en el sistema</p>
        </div>
        <Button
          variant="outline"
          onClick={onClose}
          className="hover:bg-red-50 hover:border-red-200 hover:text-red-600 bg-transparent"
        >
          <X className="w-4 h-4 mr-2" />
          Cancelar
        </Button>
      </div>

      <form onSubmit={handleSubmit}>
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Información Personal</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Nombre Completo *</Label>
                <Input
                  id="name"
                  required
                  placeholder="Ej: María González"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="birthDate">Fecha de Nacimiento *</Label>
                <Input
                  id="birthDate"
                  type="date"
                  required
                  value={formData.birthDate}
                  onChange={(e) => setFormData({ ...formData, birthDate: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="gender">Género *</Label>
                <Select
                  value={formData.gender}
                  onValueChange={(value: "masculino" | "femenino") => setFormData({ ...formData, gender: value })}
                >
                  <SelectTrigger className="border-amber-200 focus:border-amber-400">
                    <SelectValue placeholder="Seleccionar género" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="masculino">Masculino</SelectItem>
                    <SelectItem value="femenino">Femenino</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="community">Comunidad *</Label>
                <Input
                  id="community"
                  required
                  placeholder="Ej: Villa Esperanza"
                  value={formData.community}
                  onChange={(e) => setFormData({ ...formData, community: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="guardian">Nombre del Acudiente *</Label>
                <Input
                  id="guardian"
                  required
                  placeholder="Ej: Ana González"
                  value={formData.guardian}
                  onChange={(e) => setFormData({ ...formData, guardian: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Teléfono de Contacto</Label>
                <Input
                  id="phone"
                  placeholder="Ej: +57 300 123 4567"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Dirección</Label>
              <Input
                id="address"
                placeholder="Ej: Calle 15 #23-45"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="border-amber-200 focus:border-amber-400"
              />
            </div>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500 mt-6`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Mediciones Iniciales</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="weight">Peso (kg)</Label>
                <Input
                  id="weight"
                  type="number"
                  step="0.1"
                  placeholder="15.2"
                  value={formData.weight}
                  onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="height">Talla (cm)</Label>
                <Input
                  id="height"
                  type="number"
                  step="0.1"
                  placeholder="98.5"
                  value={formData.height}
                  onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                  className="border-amber-200 focus:border-amber-400"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="observations">Observaciones Iniciales</Label>
              <Textarea
                id="observations"
                placeholder="Registra observaciones sobre el estado inicial del niño..."
                value={formData.observations}
                onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
                className="min-h-[100px] border-amber-200 focus:border-amber-400"
              />
            </div>

            <div className="flex gap-4 pt-4">
              <Button
                type="submit"
                className={`flex-1 bg-gradient-to-r ${theme.buttonColor} text-white transition-all duration-300 hover:scale-105`}
              >
                <Save className="w-4 h-4 mr-2" />
                Registrar Niño
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className={`${theme.cardBorder} flex-1 hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
              >
                Cancelar
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
