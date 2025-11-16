"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Save, X, Plus, Search, Check, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "sonner"
import type { ThemeColors } from "@/types"

interface NewChildFormProps {
  theme: ThemeColors
  onClose: () => void
  onSave: (childData: any) => void
}

interface Sede {
  id_sede: number
  nombre: string
  municipio?: string
  departamento?: string
}

interface Acudiente {
  id_acudiente: number
  nombre: string
  telefono?: string
  correo?: string
  direccion?: string
}

export function NewChildForm({ theme, onClose, onSave }: NewChildFormProps) {
  const [sedes, setSedes] = useState<Sede[]>([])
  const [acudientes, setAcudientes] = useState<Acudiente[]>([])
  const [loadingSedes, setLoadingSedes] = useState(true)
  const [loadingAcudientes, setLoadingAcudientes] = useState(true)
  const [showAcudienteForm, setShowAcudienteForm] = useState(false)
  const [searchAcudiente, setSearchAcudiente] = useState("")
  const [savingAcudiente, setSavingAcudiente] = useState(false)
  const [savingChild, setSavingChild] = useState(false)
  
  const [formData, setFormData] = useState({
    name: "",
    birthDate: "",
    gender: "",
    sedeId: "",
    acudienteId: "",
    weight: "",
    height: "",
    observations: "",
  })

  const [acudienteForm, setAcudienteForm] = useState({
    nombre: "",
    telefono: "",
    correo: "",
    direccion: "",
  })

  // Cargar sedes desde la API
  useEffect(() => {
    const fetchSedes = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
        const response = await fetch(`${apiBase}/api/sedes/`)
        
        if (response.ok) {
          const data = await response.json()
          setSedes(data)
        } else {
          console.error("Error al cargar sedes")
        }
      } catch (error) {
        console.error("Error de conexión al cargar sedes:", error)
      } finally {
        setLoadingSedes(false)
      }
    }

    fetchSedes()
  }, [])

  // Cargar acudientes desde la API
  useEffect(() => {
    const fetchAcudientes = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
        const url = searchAcudiente 
          ? `${apiBase}/api/acudientes/?search=${encodeURIComponent(searchAcudiente)}`
          : `${apiBase}/api/acudientes/`
        
        const response = await fetch(url)
        
        if (response.ok) {
          const data = await response.json()
          setAcudientes(data)
        } else {
          console.error("Error al cargar acudientes")
        }
      } catch (error) {
        console.error("Error de conexión al cargar acudientes:", error)
      } finally {
        setLoadingAcudientes(false)
      }
    }

    const timeoutId = setTimeout(() => {
      fetchAcudientes()
    }, 300) // Debounce de 300ms

    return () => clearTimeout(timeoutId)
  }, [searchAcudiente])

  const handleCreateAcudiente = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (savingAcudiente) return // Prevenir doble clic
    
    setSavingAcudiente(true)
    
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
      const response = await fetch(`${apiBase}/api/acudientes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(acudienteForm),
      })

      if (response.ok) {
        const newAcudiente = await response.json()
        setAcudientes([...acudientes, newAcudiente])
        setFormData({ ...formData, acudienteId: newAcudiente.id_acudiente.toString() })
        setShowAcudienteForm(false)
        setAcudienteForm({ nombre: "", telefono: "", correo: "", direccion: "" })
        
        toast.success("¡Acudiente registrado!", {
          description: `${newAcudiente.nombre} ha sido registrado exitosamente.`,
          duration: 3000,
        })
      } else {
        const error = await response.json()
        toast.error("Error al registrar", {
          description: error.detail || 'No se pudo registrar el acudiente',
          duration: 4000,
        })
      }
    } catch (error) {
      console.error(error)
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor",
        duration: 4000,
      })
    } finally {
      setSavingAcudiente(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (savingChild) return // Prevenir doble clic
    
    setSavingChild(true)

    const payload = {
      nombre: formData.name,
      fecha_nacimiento: formData.birthDate,
      genero: formData.gender === "masculino" ? "M" : "F",
      sede_id: formData.sedeId ? parseInt(formData.sedeId) : null,
      acudiente_id: formData.acudienteId ? parseInt(formData.acudienteId) : null,
    };

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
      const response = await fetch(`${apiBase}/api/children/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        
        toast.success("¡Niño registrado exitosamente!", {
          description: `${formData.name} ha sido agregado al sistema.`,
          duration: 3000,
        })
        
        // Esperar un momento para que se vea el toast antes de cerrar
        setTimeout(() => {
          onSave(data);
          onClose();
        }, 1000)
      } else {
        const error = await response.json();
        toast.error("Error al registrar el niño", {
          description: error.detail || 'No se pudo registrar el niño',
          duration: 4000,
        })
      }
    } catch (error) {
      console.error(error);
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor",
        duration: 4000,
      })
    } finally {
      setSavingChild(false)
    }
  };

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
                <Label htmlFor="sede">Comunidad *</Label>
                <Select
                  value={formData.sedeId}
                  onValueChange={(value) => setFormData({ ...formData, sedeId: value })}
                  disabled={loadingSedes}
                >
                  <SelectTrigger className="border-amber-200 focus:border-amber-400">
                    <SelectValue placeholder={loadingSedes ? "Cargando sedes..." : "Seleccionar sede"} />
                  </SelectTrigger>
                  <SelectContent>
                    {sedes.length === 0 && !loadingSedes ? (
                      <SelectItem value="none" disabled>No hay sedes disponibles</SelectItem>
                    ) : (
                      sedes.map((sede) => (
                        <SelectItem key={sede.id_sede} value={sede.id_sede.toString()}>
                          {sede.nombre}
                          {sede.municipio && ` - ${sede.municipio}`}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="acudiente">Acudiente *</Label>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => setShowAcudienteForm(!showAcudienteForm)}
                  className="text-xs"
                  disabled={savingAcudiente}
                >
                  <Plus className="w-3 h-3 mr-1" />
                  Registrar Nuevo
                </Button>
              </div>
              
              {showAcudienteForm ? (
                <Card className="border-2 border-amber-300 bg-amber-50/50 p-4 space-y-4">
                  <h3 className="font-semibold text-sm text-slate-700">Registrar Nuevo Acudiente</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="acudiente-nombre" className="text-xs">Nombre Completo *</Label>
                      <Input
                        id="acudiente-nombre"
                        required
                        placeholder="Ej: Ana González"
                        value={acudienteForm.nombre}
                        onChange={(e) => setAcudienteForm({ ...acudienteForm, nombre: e.target.value })}
                        className="h-9 text-sm"
                        disabled={savingAcudiente}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="acudiente-telefono" className="text-xs">Teléfono</Label>
                      <Input
                        id="acudiente-telefono"
                        placeholder="Ej: 3001234567"
                        value={acudienteForm.telefono}
                        onChange={(e) => setAcudienteForm({ ...acudienteForm, telefono: e.target.value })}
                        className="h-9 text-sm"
                        disabled={savingAcudiente}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="acudiente-correo" className="text-xs">Correo</Label>
                      <Input
                        id="acudiente-correo"
                        type="email"
                        placeholder="Ej: ana@example.com"
                        value={acudienteForm.correo}
                        onChange={(e) => setAcudienteForm({ ...acudienteForm, correo: e.target.value })}
                        className="h-9 text-sm"
                        disabled={savingAcudiente}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="acudiente-direccion" className="text-xs">Dirección</Label>
                      <Input
                        id="acudiente-direccion"
                        placeholder="Ej: Calle 15 #23-45"
                        value={acudienteForm.direccion}
                        onChange={(e) => setAcudienteForm({ ...acudienteForm, direccion: e.target.value })}
                        className="h-9 text-sm"
                        disabled={savingAcudiente}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      onClick={handleCreateAcudiente}
                      className="bg-amber-600 hover:bg-amber-700 text-white"
                      disabled={savingAcudiente || !acudienteForm.nombre}
                    >
                      {savingAcudiente ? (
                        <>
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Guardando...
                        </>
                      ) : (
                        <>
                          <Save className="w-3 h-3 mr-1" />
                          Guardar Acudiente
                        </>
                      )}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => setShowAcudienteForm(false)}
                      disabled={savingAcudiente}
                    >
                      Cancelar
                    </Button>
                  </div>
                </Card>
              ) : (
                <>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <Input
                      placeholder="Buscar acudiente por nombre..."
                      value={searchAcudiente}
                      onChange={(e) => setSearchAcudiente(e.target.value)}
                      className="pl-10 border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <Select
                    value={formData.acudienteId}
                    onValueChange={(value) => setFormData({ ...formData, acudienteId: value })}
                    disabled={loadingAcudientes}
                  >
                    <SelectTrigger className="border-amber-200 focus:border-amber-400">
                      <SelectValue placeholder={loadingAcudientes ? "Cargando acudientes..." : "Seleccionar acudiente"} />
                    </SelectTrigger>
                    <SelectContent>
                      {acudientes.length === 0 && !loadingAcudientes ? (
                        <SelectItem value="none" disabled>No hay acudientes disponibles</SelectItem>
                      ) : (
                        acudientes.map((acudiente) => (
                          <SelectItem key={acudiente.id_acudiente} value={acudiente.id_acudiente.toString()}>
                            {acudiente.nombre}
                            {acudiente.telefono && ` - ${acudiente.telefono}`}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500 mt-6`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Mediciones Iniciales (Opcional)</CardTitle>
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
                  disabled={savingChild}
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
                  disabled={savingChild}
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
                disabled={savingChild}
              />
            </div>

            <div className="flex gap-4 pt-4">
              <Button
                type="submit"
                className={`flex-1 bg-gradient-to-r ${theme.buttonColor} text-white transition-all duration-300 hover:scale-105`}
                disabled={savingChild}
              >
                {savingChild ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Registrando...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Registrar Niño
                  </>
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className={`${theme.cardBorder} flex-1 hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
                disabled={savingChild}
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