"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Save, X, Plus, Search, Loader2, Pencil, Trash2 } from "lucide-react"
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
  editingChild?: {
    id_infante: number
    nombre: string
    fecha_nacimiento: string
    genero: string
    sede_id: number | null
    acudiente_id: number | null
  } | null
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

export function NewChildForm({ theme, onClose, onSave, editingChild }: NewChildFormProps) {
  const [sedes, setSedes] = useState<Sede[]>([])
  const [acudientes, setAcudientes] = useState<Acudiente[]>([])
  const [loadingSedes, setLoadingSedes] = useState(true)
  const [loadingAcudientes, setLoadingAcudientes] = useState(true)
  const [acudienteFormMode, setAcudienteFormMode] = useState<"create" | "edit" | null>(null)
  const [editingAcudienteId, setEditingAcudienteId] = useState<number | null>(null)
  const [searchAcudiente, setSearchAcudiente] = useState("")
  const [savingAcudiente, setSavingAcudiente] = useState(false)
  const [deletingAcudiente, setDeletingAcudiente] = useState(false)
  const [savingChild, setSavingChild] = useState(false)
  
  const [formData, setFormData] = useState({
    name: editingChild?.nombre || "",
    birthDate: editingChild?.fecha_nacimiento || "",
    gender: editingChild?.genero === "M" ? "masculino" : editingChild?.genero === "F" ? "femenino" : "",
    sedeId: editingChild?.sede_id?.toString() || "",
    acudienteId: editingChild?.acudiente_id?.toString() || "",
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
        const response = await fetch(`/api/sedes`)
        
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
      setLoadingAcudientes(true)
      try {
        const url = searchAcudiente 
          ? `/api/acudientes?search=${encodeURIComponent(searchAcudiente)}`
          : `/api/acudientes`
        
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

  const resetAcudienteForm = () => {
    setAcudienteForm({ nombre: "", telefono: "", correo: "", direccion: "" })
    setEditingAcudienteId(null)
  }

  const openCreateAcudienteForm = () => {
    resetAcudienteForm()
    setAcudienteFormMode("create")
  }

  const openEditAcudienteForm = () => {
    if (!formData.acudienteId) {
      toast.info("Selecciona un acudiente para editar", { duration: 3000 })
      return
    }

    const acudiente = acudientes.find(
      (item) => item.id_acudiente.toString() === formData.acudienteId
    )

    if (!acudiente) {
      toast.error("No se encontró el acudiente seleccionado", { duration: 4000 })
      return
    }

    setAcudienteForm({
      nombre: acudiente.nombre || "",
      telefono: acudiente.telefono || "",
      correo: acudiente.correo || "",
      direccion: acudiente.direccion || "",
    })
    setEditingAcudienteId(acudiente.id_acudiente)
    setAcudienteFormMode("edit")
  }

  const closeAcudienteForm = () => {
    setAcudienteFormMode(null)
    resetAcudienteForm()
  }

  const handleSaveAcudiente = async () => {
    if (savingAcudiente || !acudienteFormMode) return

    const isEditMode = acudienteFormMode === "edit"

    if (isEditMode && !editingAcudienteId) {
      toast.error("No se ha seleccionado un acudiente para editar", { duration: 4000 })
      return
    }

    setSavingAcudiente(true)

    try {
      const url = isEditMode
        ? `/api/acudientes/${editingAcudienteId}`
        : `/api/acudientes`

      const response = await fetch(url, {
        method: isEditMode ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(acudienteForm),
      })

      if (response.ok) {
        const updatedAcudiente = await response.json()

        if (isEditMode) {
          setAcudientes(
            acudientes.map((item) =>
              item.id_acudiente === updatedAcudiente.id_acudiente ? updatedAcudiente : item
            )
          )
          toast.success("Acudiente actualizado", {
            description: `${updatedAcudiente.nombre} ha sido actualizado.`,
            duration: 3000,
          })
        } else {
          setAcudientes([...acudientes, updatedAcudiente])
          setFormData({ ...formData, acudienteId: updatedAcudiente.id_acudiente.toString() })
          toast.success("¡Acudiente registrado!", {
            description: `${updatedAcudiente.nombre} ha sido registrado exitosamente.`,
            duration: 3000,
          })
        }

        closeAcudienteForm()
      } else {
        const error = await response.json()
        toast.error(isEditMode ? "Error al actualizar" : "Error al registrar", {
          description: error.detail || "No se pudo completar la acción",
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

  const handleDeleteAcudiente = async () => {
    if (!formData.acudienteId || deletingAcudiente) return

    const acudiente = acudientes.find(
      (item) => item.id_acudiente.toString() === formData.acudienteId
    )

    if (!acudiente) {
      toast.error("No se encontró el acudiente seleccionado", { duration: 4000 })
      return
    }

    const confirmed = window.confirm(`¿Eliminar a ${acudiente.nombre}?`)
    if (!confirmed) return

    setDeletingAcudiente(true)

    try {
      const response = await fetch(`/api/acudientes/${acudiente.id_acudiente}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setAcudientes(acudientes.filter((item) => item.id_acudiente !== acudiente.id_acudiente))

        if (formData.acudienteId === acudiente.id_acudiente.toString()) {
          setFormData({ ...formData, acudienteId: "" })
        }

        toast.success("Acudiente eliminado", {
          description: `${acudiente.nombre} ha sido eliminado.`,
          duration: 3000,
        })
      } else {
        const error = await response.json()
        toast.error("No se pudo eliminar", {
          description: error.detail || "Ocurrió un error al eliminar el acudiente",
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
      setDeletingAcudiente(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (savingChild) return // Prevenir doble clic
    
    setSavingChild(true)

    const isEditMode = !!editingChild
    const payload = {
      nombre: formData.name,
      fecha_nacimiento: formData.birthDate,
      genero: formData.gender === "masculino" ? "M" : "F",
      sede_id: formData.sedeId ? parseInt(formData.sedeId) : null,
      acudiente_id: formData.acudienteId ? parseInt(formData.acudienteId) : null,
    };

    try {
      const url = isEditMode
        ? `/api/children/${editingChild.id_infante}`
        : `/api/children`
      
      const response = await fetch(url, {
        method: isEditMode ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        
        toast.success(isEditMode ? "¡Niño actualizado exitosamente!" : "¡Niño registrado exitosamente!", {
          description: `${formData.name} ha sido ${isEditMode ? "actualizado" : "agregado"} al sistema.`,
          duration: 3000,
        })
        
        // Esperar un momento para que se vea el toast antes de cerrar
        setTimeout(() => {
          onSave(data);
          onClose();
        }, 1000)
      } else {
        const error = await response.json();
        toast.error(isEditMode ? "Error al actualizar el niño" : "Error al registrar el niño", {
          description: error.detail || `No se pudo ${isEditMode ? "actualizar" : "registrar"} el niño`,
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
          <h1 className="text-2xl font-bold text-slate-800 mb-2">
            {editingChild ? "Editar Niño" : "Registrar Nuevo Niño"}
          </h1>
          <p className="text-slate-600">
            {editingChild ? "Modifica la información del niño" : "Ingresa la información del nuevo niño en el sistema"}
          </p>
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
                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={openCreateAcudienteForm}
                    className="text-xs"
                    disabled={savingAcudiente}
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    Registrar Nuevo
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={openEditAcudienteForm}
                    className="text-xs"
                    disabled={!formData.acudienteId || savingAcudiente}
                  >
                    <Pencil className="w-3 h-3 mr-1" />
                    Editar
                  </Button>
                </div>
              </div>
              
              {acudienteFormMode ? (
                <Card className="border-2 border-amber-300 bg-amber-50/50 p-4 space-y-4">
                  <h3 className="font-semibold text-sm text-slate-700">
                    {acudienteFormMode === "edit" ? "Editar Acudiente" : "Registrar Nuevo Acudiente"}
                  </h3>
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
                      onClick={handleSaveAcudiente}
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
                          {acudienteFormMode === "edit" ? "Guardar Cambios" : "Guardar Acudiente"}
                        </>
                      )}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={closeAcudienteForm}
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
                  <div className="flex items-center gap-2 pt-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={handleDeleteAcudiente}
                      disabled={!formData.acudienteId || deletingAcudiente}
                      className="text-xs border-red-200 text-red-600 hover:bg-red-50"
                    >
                      {deletingAcudiente ? (
                        <>
                          <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                          Eliminando...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-3 h-3 mr-1" />
                          Eliminar
                        </>
                      )}
                    </Button>
                  </div>
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
                    {editingChild ? "Actualizando..." : "Registrando..."}
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    {editingChild ? "Actualizar Niño" : "Registrar Niño"}
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