"use client"

import { useState, useEffect } from "react"
import { FileText, Download, AlertTriangle, CheckCircle, User, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { Child, ThemeColors } from "@/types"
import { toast } from "sonner"

interface FollowUpResultsProps {
  child: Child
  followUpData: any
  theme: ThemeColors
  onClose: () => void
  onSaveToProfile: () => void
}

interface AssessmentData {
  assessment: {
    bmi: number
    weight_for_age_zscore: number
    height_for_age_zscore: number
    bmi_for_age_zscore: number
    head_circumference_zscore: number | null
    triceps_skinfold_zscore: number | null
    subscapular_skinfold_zscore: number | null
    nutritional_status: {
      peso_edad: string
      talla_edad: string
      peso_talla: string
      imc_edad: string
      perimetro_cefalico_edad?: string
      pliegue_triceps?: string
      pliegue_subescapular?: string
    }
    risk_level: string
  }
  energy_requirements: {
    total_energy_kcal: number
    per_kg_kcal?: number
  }
  nutrient_requirements: any[]
  recommendations: {
    nutritional_recommendations: string[]
    general_recommendations: string[]
    caregiver_instructions: string[]
  }
}

export function FollowUpResults({ child, followUpData, theme, onClose, onSaveToProfile }: FollowUpResultsProps) {
  const [activeTab, setActiveTab] = useState("results")
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null)
  const [loadingAssessment, setLoadingAssessment] = useState(true)

  // **AQUÍ VA EL useEffect - después de declarar los estados**
  useEffect(() => {
    const fetchEvaluacion = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
        
        // Obtener el ID del seguimiento desde sessionStorage
        const seguimientoId = sessionStorage.getItem('last_seguimiento_id')
        
        if (!seguimientoId) {
          console.error("No hay ID de seguimiento")
          toast.error("Error", {
            description: "No se encontró el ID del seguimiento"
          })
          setLoadingAssessment(false)
          return
        }
        
        console.log("Cargando evaluación para seguimiento:", seguimientoId)
        
        const response = await fetch(`${apiBase}/api/followups/${seguimientoId}/evaluacion`)
        
        if (response.ok) {
          const data = await response.json()
          console.log("Evaluación cargada:", data)
          setAssessmentData(data)
        } else {
          const error = await response.json()
          console.error("Error al cargar evaluación:", error)
          toast.error("Error al cargar evaluación", {
            description: error.detail || "No se pudo cargar la evaluación nutricional"
          })
        }
      } catch (error) {
        console.error("Error de conexión:", error)
        toast.error("Error de conexión", {
          description: "No se pudo conectar con el servidor"
        })
      } finally {
        setLoadingAssessment(false)
      }
    }
    
    fetchEvaluacion()
  }, []) // Array vacío para que solo se ejecute una vez al montar

  // Usar datos reales si están disponibles, sino usar simulados
  const riskLevel = assessmentData?.assessment.risk_level || "Bajo"
  const nutritionalStatus = assessmentData?.assessment.nutritional_status || {
    peso_edad: "Normal",
    talla_edad: "Normal",
    imc_edad: "Normal"
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Alto":
        return "bg-red-100 text-red-800"
      case "Medio":
        return "bg-orange-100 text-orange-800"
      case "Bajo":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getGeneralStatus = (risk: string) => {
    switch (risk) {
      case "Alto":
        return "Requiere atención médica urgente"
      case "Medio":
        return "Requiere seguimiento cercano"
      case "Bajo":
        return "Niño aparentemente sano"
      default:
        return "Estado no determinado"
    }
  }

  const calculateAgeDays = (birthDate: string): number => {
    const today = new Date()
    const birth = new Date(birthDate)
    const diffTime = Math.abs(today.getTime() - birth.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const generateClinicalPDF = async () => {
    setIsGeneratingPDF(true)
    
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
      const ageDays = calculateAgeDays(child.birthDate)
      
      const observaciones = []
      if (followUpData.symptoms && followUpData.symptoms.length > 0) {
        observaciones.push(`Síntomas: ${followUpData.symptoms.join(', ')}`)
      }
      if (followUpData.physicalSigns && followUpData.physicalSigns.length > 0) {
        observaciones.push(`Signos físicos: ${followUpData.physicalSigns.join(', ')}`)
      }
      if (followUpData.clinicalObservations) {
        observaciones.push(followUpData.clinicalObservations)
      }
      
      const observacionesTexto = observaciones.length > 0 
        ? observaciones.join('. ') 
        : 'Sin observaciones'
      
      const params = new URLSearchParams({
        name: child.name,
        age_days: ageDays.toString(),
        weight: followUpData.weight || '0',
        height: followUpData.height || '0',
        gender: child.gender === 'masculino' ? 'male' : 'female',
        head_circumference: followUpData.headCircumference || '0',
        triceps_skinfold: followUpData.tricepsFold || '0',
        subscapular_skinfold: '0',
        activity_level: 'moderate',
        feeding_mode: 'mixed',
        nutricionist_observation: observacionesTexto
      })
      
      const url = `${apiBase}/api/nutrition/nutritional-report?${params.toString()}`
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error('Error al generar el reporte')
      }
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `${child.name.replace(' ', '_')}_reporte_clinico_${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(downloadUrl)
      
      toast.success("Reporte generado exitosamente", {
        description: "El PDF ha sido descargado",
        duration: 3000,
      })
      
    } catch (error) {
      console.error("Error generando PDF:", error)
      toast.error("Error al generar reporte", {
        description: "No se pudo generar el PDF. Verifica los datos.",
        duration: 5000,
      })
    } finally {
      setIsGeneratingPDF(false)
    }
  }

  const handleSave = () => {
    onSaveToProfile()
    toast.success("Resultados guardados", {
      description: "Los resultados se han guardado en el perfil del niño",
      duration: 3000,
    })
  }

  // Mostrar loading mientras carga la evaluación
  if (loadingAssessment) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-slate-600">Cargando evaluación nutricional...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con información del niño */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Avatar className="w-16 h-16">
                <AvatarFallback className="bg-gradient-to-br from-blue-400 to-blue-500 text-white font-bold text-lg">
                  {child.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">Resultados de Evaluación</h2>
                <p className="text-lg text-slate-600">
                  {child.name} • {child.age}
                </p>
                <p className="text-sm text-slate-500">Fecha de evaluación: {new Date().toLocaleDateString()}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose}>
                Cerrar
              </Button>
              <Button onClick={handleSave} className={`bg-gradient-to-r ${theme.buttonColor} text-white`}>
                Guardar en Perfil
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="results">Resultados</TabsTrigger>
          <TabsTrigger value="nutrition">Recomendaciones Nutricionales</TabsTrigger>
          <TabsTrigger value="general">Recomendaciones Generales</TabsTrigger>
          <TabsTrigger value="caregiver">Para el Cuidador</TabsTrigger>
        </TabsList>

        <TabsContent value="results" className="space-y-6">
          {/* Clasificación nutricional CON DATOS REALES */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Clasificación Nutricional
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Nivel de Riesgo:</span>
                    <Badge className={getRiskColor(riskLevel)}>
                      {riskLevel}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Peso/Edad:</span>
                    <Badge variant="outline">{nutritionalStatus.peso_edad}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Talla/Edad:</span>
                    <Badge variant="outline">{nutritionalStatus.talla_edad}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">IMC/Edad:</span>
                    <Badge variant="outline">{nutritionalStatus.imc_edad}</Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-slate-700">Estado General:</span>
                    <p className="text-sm text-slate-600 mt-1">{getGeneralStatus(riskLevel)}</p>
                  </div>
                  {assessmentData && (
                    <div>
                      <span className="font-medium text-slate-700">Z-Scores:</span>
                      <div className="text-xs text-slate-600 mt-1 space-y-1">
                        <p>Peso/Edad: {assessmentData.assessment.weight_for_age_zscore?.toFixed(2) || 'N/A'}</p>
                        <p>Talla/Edad: {assessmentData.assessment.height_for_age_zscore?.toFixed(2) || 'N/A'}</p>
                        <p>IMC/Edad: {assessmentData.assessment.bmi_for_age_zscore?.toFixed(2) || 'N/A'}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Datos antropométricos */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800">Análisis Antropométrico</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-slate-800">{followUpData.weight || "N/A"}</div>
                  <div className="text-sm text-slate-600">Peso (kg)</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-slate-800">{followUpData.height || "N/A"}</div>
                  <div className="text-sm text-slate-600">Talla (cm)</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-slate-800">
                    {assessmentData?.assessment.bmi?.toFixed(1) || "N/A"}
                  </div>
                  <div className="text-sm text-slate-600">IMC</div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg border">
                  <div className="text-2xl font-bold text-slate-800">{child.age}</div>
                  <div className="text-sm text-slate-600">Edad</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Requerimientos Energéticos */}
          {assessmentData?.energy_requirements && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Requerimientos Energéticos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-white rounded-lg border">
                    <div className="text-3xl font-bold text-purple-600">
                      {assessmentData.energy_requirements.total_energy_kcal?.toFixed(0) || 'N/A'}
                    </div>
                    <div className="text-sm text-slate-600">kcal/día</div>
                  </div>
                  {assessmentData.energy_requirements.per_kg_kcal && (
                    <div className="text-center p-4 bg-white rounded-lg border">
                      <div className="text-3xl font-bold text-purple-600">
                        {assessmentData.energy_requirements.per_kg_kcal?.toFixed(1)}
                      </div>
                      <div className="text-sm text-slate-600">kcal/kg/día</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="nutrition" className="space-y-6">
          {/* Mostrar recomendaciones reales si están disponibles */}
          {assessmentData?.recommendations ? (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Recomendaciones Nutricionales</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {assessmentData.recommendations.nutritional_recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-slate-700">{rec}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="text-center text-slate-500">
              Cargando recomendaciones...
            </div>
          )}

          {/* Requerimientos de Nutrientes */}
          {assessmentData?.nutrient_requirements && assessmentData.nutrient_requirements.length > 0 && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Requerimientos Diarios de Nutrientes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {assessmentData.nutrient_requirements.slice(0, 12).map((nutrient: any, index: number) => (
                    <div key={index} className="p-3 bg-white rounded-lg border">
                      <div className="font-medium text-slate-700 text-sm">{nutrient.nutriente || nutrient.name}</div>
                      <div className="text-lg font-bold text-blue-600">
                        {nutrient.valor_recomendado || nutrient.recommended_value}
                      </div>
                      <div className="text-xs text-slate-500">{nutrient.unidad || nutrient.unit}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="general" className="space-y-6">
          {assessmentData?.recommendations?.general_recommendations && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Recomendaciones Generales</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {assessmentData.recommendations.general_recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-slate-700">{rec}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="caregiver" className="space-y-6">
          {assessmentData?.recommendations?.caregiver_instructions && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-yellow-50`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Instrucciones para el Cuidador
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {assessmentData.recommendations.caregiver_instructions.map((instruction, index) => (
                  <div key={index} className="bg-white p-4 rounded-lg border border-yellow-200">
                    <p className="text-slate-700 leading-relaxed">{instruction}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Botón de reporte PDF */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
        <CardContent className="p-6">
          <div className="flex justify-center">
            <Button
              onClick={generateClinicalPDF}
              disabled={isGeneratingPDF}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 disabled:opacity-50"
            >
              {isGeneratingPDF ? (
                <>
                  <Download className="w-4 h-4 mr-2 animate-spin" />
                  Generando PDF...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Descargar Reporte Clínico PDF
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}