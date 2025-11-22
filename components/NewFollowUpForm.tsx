"use client"

import { useState, useEffect } from "react"
import { Save, Search, User, Camera, FileText, Activity, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { FileUpload } from "./FileUpload"
import { FollowUpResults } from "./FollowUpResults"
import type { ThemeColors, FollowUpForm, Child } from "@/types"
import { SYMPTOMS_OPTIONS, PHYSICAL_SIGNS_OPTIONS } from "@/types"
import { toast } from "sonner"

interface NewFollowUpFormProps {
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

export function NewFollowUpForm({ theme }: NewFollowUpFormProps) {
  const [selectedChild, setSelectedChild] = useState<Child | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [showResults, setShowResults] = useState(false)
  const [children, setChildren] = useState<Infante[]>([])
  const [loading, setLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [anemiaResult, setAnemiaResult] = useState<any>(null)
  const [predictingAnemia, setPredictingAnemia] = useState(false)
  const [formData, setFormData] = useState<FollowUpForm>({
    childId: 0,
    weight: "",
    height: "",
    armCircumference: "",
    headCircumference: "",
    tricepsFold: "",
    subscapularFold: "",
    abdominalPerimeter: "",
    symptoms: [],
    physicalSigns: [],
    clinicalObservations: "",
    hemoglobin: "",
    stoolExam: "",
    urineExam: "",
    eyePhotos: [],
    gumPhotos: [],
    caregiverComments: "",
  })

  // Cargar infantes desde la API
  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const response = await fetch(`/api/children`)
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

    fetchChildren()
  }, [])

  const filteredChildren = children.filter((child) => 
    child.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const calculateAge = (birthDate: string) => {
    const today = new Date()
    const birth = new Date(birthDate)
    const ageInMonths = (today.getFullYear() - birth.getFullYear()) * 12 + (today.getMonth() - birth.getMonth())
    const years = Math.floor(ageInMonths / 12)
    const months = ageInMonths % 12
    
    if (years > 0) {
      return `${years} año${years !== 1 ? 's' : ''} ${months} mes${months !== 1 ? 'es' : ''}`
    } else {
      return `${months} mes${months !== 1 ? 'es' : ''}`
    }
  }

  const calculateAgeInMonths = (birthDate: string): number => {
    const today = new Date()
    const birth = new Date(birthDate)
    const ageInMonths = (today.getFullYear() - birth.getFullYear()) * 12 + (today.getMonth() - birth.getMonth())
    return Math.max(0, ageInMonths)
  }

  const calculateBMI = (weight: string, height: string) => {
    if (!weight || !height) return ""
    const weightNum = Number.parseFloat(weight)
    const heightNum = Number.parseFloat(height) / 100
    if (weightNum > 0 && heightNum > 0) {
      return (weightNum / (heightNum * heightNum)).toFixed(1)
    }
    return ""
  }

  const handleChildSelect = (child: Infante) => {
    // Convertir Infante a Child
    const childData: Child = {
      id: child.id_infante,
      name: child.nombre,
      age: calculateAge(child.fecha_nacimiento),
      gender: child.genero === "M" ? "masculino" : "femenino",
      birthDate: child.fecha_nacimiento,
      community: child.sede_id ? child.sede_id.toString() : "N/A",
      guardian: child.acudiente_id ? child.acudiente_id.toString() : "N/A",
      phone: "N/A",
      address: "N/A",
      status: "normal",
      lastVisit: "N/A",
      weight: 0,
      height: 0,
      medicalHistory: [],
      growthHistory: [],
    }
    
    setSelectedChild(childData)
    setFormData({ ...formData, childId: child.id_infante })
    setSearchTerm("")
  }

  const handleSymptomChange = (symptom: string, checked: boolean) => {
    if (checked) {
      setFormData({ ...formData, symptoms: [...formData.symptoms, symptom] })
    } else {
      setFormData({ ...formData, symptoms: formData.symptoms.filter((s) => s !== symptom) })
    }
  }

  const handlePhysicalSignChange = (sign: string, checked: boolean) => {
    if (checked) {
      setFormData({ ...formData, physicalSigns: [...formData.physicalSigns, sign] })
    } else {
      setFormData({ ...formData, physicalSigns: formData.physicalSigns.filter((s) => s !== sign) })
    }
  }

  const handleEyePhotosChange = (files: File[]) => {
    setFormData({ ...formData, eyePhotos: files })
    
    // Automáticamente predecir anemia si hay archivo y edad disponible
    if (files.length > 0 && selectedChild) {
      predictAnemiaFromImage(files[0])
    }
  }

  const predictAnemiaFromImage = async (file: File) => {
    if (!selectedChild) return
    
    setPredictingAnemia(true)
    const ageMonths = calculateAgeInMonths(selectedChild.birthDate)
    
    try {
      const formDataToSend = new FormData()
      formDataToSend.append('file', file)
      formDataToSend.append('age_months', ageMonths.toString())
      
      const response = await fetch('/api/vision/predict-anemia', {
        method: 'POST',
        body: formDataToSend
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log("Predicción de anemia:", result)
        setAnemiaResult(result)
        
        toast.success("Análisis de imagen completado", {
          description: `Hemoglobina estimada: ${result.hb_estimate_g_dL.toFixed(2)} g/dL - ${result.anemia_label}`
        })
      } else {
        const error = await response.json()
        console.error("Error en predicción:", error)
        toast.error("Error al procesar imagen", {
          description: error.detail || "No se pudo analizar la imagen"
        })
      }
    } catch (error) {
      console.error("Error de conexión:", error)
      toast.error("Error al conectar con el servicio")
    } finally {
      setPredictingAnemia(false)
    }
  }

  const handleGumPhotosChange = (files: File[]) => {
    setFormData({ ...formData, gumPhotos: files })
  }

  // Generar la lista de observaciones clínicas automáticamente
  const getObservacionesClinicas = () => {
    const observaciones: string[] = []
    
    if (formData.symptoms.length > 0) {
      observaciones.push(`Síntomas: ${formData.symptoms.join(', ')}`)
    }
    
    if (formData.physicalSigns.length > 0) {
      observaciones.push(`Signos físicos: ${formData.physicalSigns.join(', ')}`)
    }
    
    return observaciones
  }


  const getLocalDateString = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedChild) {
      toast.error("Error", {
        description: "Debes seleccionar un infante primero"
      })
      return
    }

    setIsSubmitting(true) // NUEVO: Bloquear botón

    try {
      const observacionesClinicas = getObservacionesClinicas()
      const ageMonths = calculateAgeInMonths(selectedChild.birthDate)
      
      // Determinar resultado de anemia con prioridad: hemoglobina > modelo
      let finalAnemiaResult = null
      
      if (formData.hemoglobin && formData.hemoglobin.trim() !== "") {
        // Si hay hemoglobina, usarla
        const hbValue = parseFloat(formData.hemoglobin)
        const threshold = ageMonths <= 59 ? 12.0 : 12.25
        finalAnemiaResult = {
          source: "hemoglobina",
          value: hbValue,
          threshold: threshold,
          isAnemic: hbValue < threshold,
          label: hbValue < threshold ? "Anémico" : "Normal"
        }
      } else if (anemiaResult) {
        // Si no hay hemoglobina pero hay resultado del modelo
        finalAnemiaResult = {
          source: "modelo",
          value: anemiaResult.hb_estimate_g_dL,
          threshold: anemiaResult.threshold_g_dL,
          isAnemic: anemiaResult.anemia_flag,
          label: anemiaResult.anemia_label
        }
      }
      
      const seguimientoData = {
        infante_id: formData.childId,
        fecha: getLocalDateString(),
        observacion: formData.clinicalObservations || "",
        observaciones_clinicas: observacionesClinicas,
        peso: parseFloat(formData.weight) || null,
        estatura: parseFloat(formData.height) || null,
        circunferencia_braquial: parseFloat(formData.armCircumference) || null,
        perimetro_cefalico: parseFloat(formData.headCircumference) || null,
        pliegue_triceps: parseFloat(formData.tricepsFold) || null,
        pliegue_subescapular: parseFloat(formData.subscapularFold) || null,
        perimetro_abdominal: parseFloat(formData.abdominalPerimeter) || null,
        hemoglobina: parseFloat(formData.hemoglobin) || null,
        foto_ojo_url: null,
        // Agregar resultado de anemia
        anemia_result: finalAnemiaResult
      }

      console.log("Enviando seguimiento:", seguimientoData)
      console.log("ID del infante:", formData.childId)
      
      const response = await fetch(`/api/followups`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(seguimientoData)
      })

      if (response.ok) {
        const result = await response.json()
        console.log("Seguimiento creado exitosamente:", result)
        
        sessionStorage.setItem('last_seguimiento_id', result.id_seguimiento.toString())
        // Guardar resultado de anemia para mostrar en resultados
        if (finalAnemiaResult) {
          sessionStorage.setItem('anemia_result', JSON.stringify(finalAnemiaResult))
        }
        
        toast.success("¡Seguimiento registrado exitosamente!", {
          description: `Se realizó un seguimiento nutricional a ${selectedChild.name}`,
          duration: 4000,
        })
        
        setShowResults(true)
      } else {
        const error = await response.json()
        console.error("Error al crear seguimiento:", error)
        toast.error("Error al registrar seguimiento", {
          description: error.detail || 'Error desconocido',
          duration: 5000,
        })
      }
    } catch (error) {
      console.error("Error de conexión:", error)
      toast.error("Error de conexión", {
        description: "No se pudo conectar con el servidor. Verifica tu conexión.",
        duration: 5000,
      })
    } finally {
      setIsSubmitting(false) // NUEVO: Desbloquear botón
    }
  }

  const handleSaveToProfile = () => {
    setShowResults(false)
    setSelectedChild(null) // NUEVO: Resetear para volver a la lista
    setAnemiaResult(null)  // Resetear resultado de anemia
    setFormData({
      childId: 0,
      weight: "",
      height: "",
      armCircumference: "",
      headCircumference: "",
      tricepsFold: "",
      subscapularFold: "",
      abdominalPerimeter: "",
      symptoms: [],
      physicalSigns: [],
      clinicalObservations: "",
      hemoglobin: "",
      stoolExam: "",
      urineExam: "",
      eyePhotos: [],
      gumPhotos: [],
      caregiverComments: "",
    })
  }

  const getInitials = (nombre: string): string => {
    return nombre
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
      .toUpperCase()
  }

  if (showResults && selectedChild) {
    return (
      <FollowUpResults
        child={selectedChild}
        followUpData={formData}
        theme={theme}
        onClose={() => setShowResults(false)}
        onSaveToProfile={handleSaveToProfile}
      />
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Nuevo Seguimiento</h1>
        <p className="text-lg text-slate-600">Registra una nueva evaluación nutricional completa</p>
      </div>

      {/* Selección de niño */}
      {!selectedChild ? (
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <User className="w-5 h-5" />
              Seleccionar Infante
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder="Buscar infante por nombre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-amber-200 focus:border-amber-400"
              />
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
                <span className="ml-3 text-slate-600">Cargando infantes...</span>
              </div>
            ) : filteredChildren.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-600">
                  {searchTerm
                    ? "No se encontraron infantes con ese nombre"
                    : "No hay infantes registrados"}
                </p>
              </div>
            ) : (
              <div className="grid gap-3 max-h-96 overflow-y-auto">
                {filteredChildren.map((child) => (
                  <div
                    key={child.id_infante}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
                    onClick={() => handleChildSelect(child)}
                  >
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10">
                        <AvatarFallback className="bg-gradient-to-br from-blue-400 to-blue-500 text-white font-bold text-sm">
                          {getInitials(child.nombre)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h4 className="font-semibold text-slate-800">{child.nombre}</h4>
                        <p className="text-sm text-slate-600">
                          {calculateAge(child.fecha_nacimiento)} • {child.genero === "M" ? "Masculino" : "Femenino"}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {!loading && filteredChildren.length > 0 && (
              <div className="text-center text-sm text-slate-600">
                Mostrando {filteredChildren.length} de {children.length} infante{children.length !== 1 ? 's' : ''}
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Niño seleccionado */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback className="bg-gradient-to-br from-blue-400 to-blue-500 text-white font-bold">
                      {getInitials(selectedChild.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{selectedChild.name}</h3>
                    <p className="text-slate-600">
                      {calculateAge(selectedChild.birthDate)} • {selectedChild.gender}
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSelectedChild(null)}
                  className="hover:bg-red-50 hover:border-red-200 hover:text-red-600"
                >
                  Cambiar infante
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Formulario de seguimiento */}
          <div className="grid gap-8">
            {/* Datos Antropométricos */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Datos Antropométricos
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="weight">Peso (kg) *</Label>
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
                    <Label htmlFor="height">Talla / Estatura (cm) *</Label>
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
                  <div className="space-y-2">
                    <Label htmlFor="bmi">IMC (calculado automáticamente)</Label>
                    <Input
                      id="bmi"
                      value={calculateBMI(formData.weight, formData.height)}
                      readOnly
                      className="bg-gray-50 border-gray-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="age">Edad (calculado automáticamente)</Label>
                    <Input
                      id="age"
                      value={calculateAge(selectedChild.birthDate)}
                      readOnly
                      className="bg-gray-50 border-gray-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="armCircumference">Circunferencia Braquial (cm)</Label>
                    <Input
                      id="armCircumference"
                      type="number"
                      step="0.1"
                      placeholder="16.5"
                      value={formData.armCircumference}
                      onChange={(e) => setFormData({ ...formData, armCircumference: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="headCircumference">Perímetro Cefálico (cm)</Label>
                    <Input
                      id="headCircumference"
                      type="number"
                      step="0.1"
                      placeholder="48.2"
                      value={formData.headCircumference}
                      onChange={(e) => setFormData({ ...formData, headCircumference: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tricepsFold">Pliegue Cutáneo Tricipital (mm)</Label>
                    <Input
                      id="tricepsFold"
                      type="number"
                      step="0.1"
                      placeholder="12.5"
                      value={formData.tricepsFold}
                      onChange={(e) => setFormData({ ...formData, tricepsFold: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subscapularFold">Pliegue Cutáneo Subescapular (mm)</Label>
                    <Input
                      id="subscapularFold"
                      type="number"
                      step="0.1"
                      placeholder="10.5"
                      value={formData.subscapularFold}
                      onChange={(e) => setFormData({ ...formData, subscapularFold: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="abdominalPerimeter">Perímetro Abdominal (cm)</Label>
                    <Input
                      id="abdominalPerimeter"
                      type="number"
                      step="0.1"
                      placeholder="52.3"
                      value={formData.abdominalPerimeter}
                      onChange={(e) => setFormData({ ...formData, abdominalPerimeter: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Observaciones Clínicas */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Observaciones Clínicas Generales
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Síntomas */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Síntomas observados o reportados</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {SYMPTOMS_OPTIONS.map((symptom) => (
                      <div key={symptom} className="flex items-center space-x-2">
                        <Checkbox
                          id={`symptom-${symptom}`}
                          checked={formData.symptoms.includes(symptom)}
                          onCheckedChange={(checked) => handleSymptomChange(symptom, checked as boolean)}
                        />
                        <Label htmlFor={`symptom-${symptom}`} className="text-sm cursor-pointer">
                          {symptom}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Signos físicos */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Signos físicos visibles</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {PHYSICAL_SIGNS_OPTIONS.map((sign) => (
                      <div key={sign} className="flex items-center space-x-2">
                        <Checkbox
                          id={`sign-${sign}`}
                          checked={formData.physicalSigns.includes(sign)}
                          onCheckedChange={(checked) => handlePhysicalSignChange(sign, checked as boolean)}
                        />
                        <Label htmlFor={`sign-${sign}`} className="text-sm cursor-pointer">
                          {sign}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Vista previa de observaciones seleccionadas */}
                {(formData.symptoms.length > 0 || formData.physicalSigns.length > 0) && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
                    <h4 className="font-semibold text-blue-900 text-sm">Observaciones clínicas registradas:</h4>
                    {getObservacionesClinicas().map((obs, idx) => (
                      <p key={idx} className="text-sm text-blue-800">• {obs}</p>
                    ))}
                  </div>
                )}

                {/* Observaciones del nutricionista */}
                <div className="space-y-2">
                  <Label htmlFor="clinicalObservations" className="text-base font-semibold">
                    Observaciones del nutricionista
                  </Label>
                  <Textarea
                    id="clinicalObservations"
                    placeholder="Escribe aquí las observaciones y notas del nutricionista sobre la evaluación..."
                    value={formData.clinicalObservations}
                    onChange={(e) => setFormData({ ...formData, clinicalObservations: e.target.value })}
                    className="min-h-[120px] border-amber-200 focus:border-amber-400"
                  />
                  <p className="text-xs text-slate-500">
                    Este campo es para las observaciones específicas del profesional nutricionista.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Exámenes Complementarios */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Exámenes Complementarios</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="hemoglobin">Hemoglobina (g/dL) - Opcional</Label>
                    <Input
                      id="hemoglobin"
                      type="number"
                      step="0.1"
                      placeholder="12.5"
                      value={formData.hemoglobin}
                      onChange={(e) => setFormData({ ...formData, hemoglobin: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                    <p className="text-xs text-slate-500">
                      Si tienes el resultado de un examen de sangre, ingresa el valor aquí. Este valor tendrá prioridad sobre la estimación por imagen.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Imágenes Clínicas */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Camera className="w-5 h-5" />
                  Fotografía Clínica para Análisis de Anemia
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 gap-6">
                  <div>
                    <FileUpload
                      id="eye-photos"
                      label="Fotografía de ojos (para análisis de hemoglobina por imagen)"
                      accept="image/*"
                      multiple={false}
                      onFilesChange={handleEyePhotosChange}
                    />
                    <p className="text-xs text-slate-500 mt-2">
                      Sube una fotografía clara de la conjuntiva (parte blanca) de los ojos del infante. Se usará IA para estimar la hemoglobina.
                    </p>
                  </div>
                  
                  {predictingAnemia && (
                    <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      <span className="text-blue-700 font-medium">Analizando imagen para detectar anemia...</span>
                    </div>
                  )}
                  
                  {anemiaResult && !predictingAnemia && (
                    <div className={`p-4 rounded-lg border-2 ${
                      anemiaResult.anemia_flag 
                        ? "bg-red-50 border-red-300" 
                        : "bg-green-50 border-green-300"
                    }`}>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-700">Análisis de imagen:</span>
                          <Badge className={anemiaResult.anemia_flag ? "bg-red-600" : "bg-green-600"}>
                            {anemiaResult.anemia_label}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-slate-600">Hb Estimada:</p>
                            <p className="font-bold text-lg">{anemiaResult.hb_estimate_g_dL.toFixed(2)} g/dL</p>
                          </div>
                          <div>
                            <p className="text-slate-600">Umbral OMS:</p>
                            <p className="font-bold text-lg">{anemiaResult.threshold_g_dL.toFixed(2)} g/dL</p>
                          </div>
                        </div>
                        <p className="text-xs text-slate-600 italic pt-2">
                          {anemiaResult.recommendation}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Botones de acción */}
            <div className="flex gap-4 justify-center pt-6">
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting} // NUEVO
                className={`px-8 py-3 bg-gradient-to-r ${theme.buttonColor} text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5 mr-2" />
                    Finalizar Seguimiento
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => setSelectedChild(null)}
                className={`px-8 py-3 ${theme.cardBorder} hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105 shadow-lg rounded-xl`}
              >
                Cancelar
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}