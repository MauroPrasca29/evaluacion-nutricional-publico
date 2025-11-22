"use client"

import { useState, useEffect } from "react"
import { FileText, Download, AlertTriangle, CheckCircle, User, Loader2, Activity, Scale, Ruler, TrendingUp, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { Child, ThemeColors } from "@/types"
import { toast } from "sonner"
import { WHOGrowthChart } from "@/components/WHOGrowthChart"

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
    kcal_per_day?: number
    kcal_per_kg?: number
    kcal_per_day_str?: string
    kcal_per_kg_str?: string
    source?: string
  }
  nutrient_requirements: any[]
  recommendations: {
    nutritional_recommendations: string[]
    general_recommendations: string[]
    caregiver_instructions: string[]
  }
  weight_info?: {
    current_weight: number
    expected_weight: number
  }
}

export function FollowUpResults({ child, followUpData, theme, onClose, onSaveToProfile }: FollowUpResultsProps) {
  const [activeTab, setActiveTab] = useState("results")
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)
  const [assessmentData, setAssessmentData] = useState<AssessmentData | null>(null)
  const [loadingAssessment, setLoadingAssessment] = useState(true)
  const [growthCharts, setGrowthCharts] = useState<{[key: string]: any}>({})
  const [loadingCharts, setLoadingCharts] = useState(false)

  useEffect(() => {
  const fetchEvaluacion = async () => {
    try {
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
      
      const response = await fetch(`/api/followups/${seguimientoId}/evaluacion`)
      
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
  }, [])

  const loadGrowthCharts = async () => {
    if (Object.keys(growthCharts).length > 0) return
    
    setLoadingCharts(true)
    try {
      const ageDays = calculateAgeDays(child.birthDate)
      const gender = child.gender === 'masculino' ? 'male' : 'female'
      
      // Calcular edad en años
      const ageYears = ageDays / 365
      
      console.log('=== INICIO CARGA DE GRÁFICAS ===')
      console.log('Edad:', ageYears, 'años')
      console.log('followUpData:', followUpData)
      console.log('assessmentData:', assessmentData)
      
      // Gráficas básicas (siempre se muestran)
      const chartTypes = [
        { name: 'peso', value: followUpData.weight },
        { name: 'talla', value: followUpData.height },
        { name: 'imc', value: assessmentData?.assessment.bmi }
      ]
      
      // Gráficas adicionales solo si edad <= 5 años (igual que en el PDF)
      if (ageYears <= 5) {
        console.log('Edad <= 5 años, agregando gráficas adicionales')
        
        chartTypes.push({ 
          name: 'perimetro_cefalico', 
          value: Number(followUpData.headCircumference) || 0 
        })
        
        chartTypes.push({ 
          name: 'pliegue_triceps', 
          value: Number(followUpData.tricepsFold) || 0 
        })
        
        chartTypes.push({ 
          name: 'pliegue_subescapular', 
          value: Number(followUpData.subscapularFold) || 0 
        })
      } else {
        console.log('Edad > 5 años, solo gráficas básicas')
      }
      
      console.log('Gráficas a cargar:', chartTypes)
      
      const charts: {[key: string]: any} = {}
      
      for (const chart of chartTypes) {
        try {
          console.log(`\nCargando gráfica: ${chart.name}, valor: ${chart.value}`)
          
          const params = new URLSearchParams({
            indicator: chart.name,
            age_days: ageDays.toString(),
            gender: gender,
            value: chart.value?.toString() || '0'
          })
          
          const url = `/api/nutrition/growth-chart-data?${params.toString()}`
          console.log('URL:', url)
          
          const response = await fetch(url)
          
          if (response.ok) {
            const data = await response.json()
            console.log(`✓ Gráfica ${chart.name} cargada. Datos:`, data)
            charts[chart.name] = data
          } else {
            const errorText = await response.text()
            console.error(`✗ Error en gráfica ${chart.name}:`, response.status, errorText)
          }
        } catch (error) {
          console.error(`✗ Error cargando gráfica ${chart.name}:`, error)
        }
      }
      
      console.log('\n=== RESULTADO FINAL ===')
      console.log('Gráficas cargadas exitosamente:', Object.keys(charts))
      console.log('Total de gráficas:', Object.keys(charts).length)
      
      setGrowthCharts(charts)
      
      if (Object.keys(charts).length === 0) {
        toast.error("No se pudieron cargar las gráficas", {
          description: "Verifica que el servidor esté funcionando correctamente"
        })
      } else {
        toast.success(`${Object.keys(charts).length} gráficas cargadas`, {
          description: "Las curvas de crecimiento están listas"
        })
      }
    } catch (error) {
      console.error("Error cargando gráficas:", error)
      toast.error("Error", {
        description: "No se pudieron cargar algunas gráficas de crecimiento"
      })
    } finally {
      setLoadingCharts(false)
    }
  }

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

  const getStatusColor = (status: string) => {
    if (!status) return "text-gray-600"
    const statusLower = status.toLowerCase()
    
    // Casos críticos (rojo)
    if (statusLower.includes("desnutrición") || statusLower.includes("severa") || statusLower.includes("muy bajo")) {
      return "text-red-600 font-bold"
    }
    
    // Casos de alerta (naranja) - AGREGADO "baja" y "retraso"
    if (statusLower.includes("riesgo") || 
        statusLower.includes("bajo") || 
        statusLower.includes("baja") ||
        statusLower.includes("retraso") ||
        statusLower.includes("moderada") ||
        statusLower.includes("alto") || 
        statusLower.includes("obesidad") || 
        statusLower.includes("sobrepeso")) {
      return "text-orange-600 font-semibold"
    }
    
    // Normal (verde)
    return "text-green-600"
  }

  const getRangoReferencia = (indicator: string) => {
    const rangos: { [key: string]: string } = {
      "peso_edad": "-1 ≤ z ≤ +1",
      "talla_edad": "-1 ≤ z ≤ +1",
      "peso_talla": "-1 ≤ z ≤ +1",
      "imc_edad": "-1 ≤ z ≤ +1",
      "perimetro_cefalico_edad": "-2 ≤ z ≤ +2",
      "pliegue_triceps": "-1 ≤ z ≤ +1",
      "pliegue_subescapular": "-1 ≤ z ≤ +1"
    }
    return rangos[indicator] || "-1 ≤ z ≤ +1"
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
      
      const url = `/api/nutrition/nutritional-report?${params.toString()}`
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
                  {child.name.split(" ").map((n) => n[0]).join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">{child.name}</h2>
                <p className="text-slate-600">
                  {child.age} • {child.gender}
                </p>
                <Badge className={`mt-2 ${getRiskColor(riskLevel)}`}>
                  Nivel de Riesgo: {riskLevel}
                </Badge>
              </div>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={onSaveToProfile}  // CAMBIAR: de onClose a onSaveToProfile
                className={`${theme.cardBorder} hover:bg-opacity-50`}
              >
                Cerrar
              </Button>
              <Button
                onClick={generateClinicalPDF}
                disabled={isGeneratingPDF}
                className="bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:scale-105 transition-transform hover:from-blue-600 hover:to-blue-700"              >
                {isGeneratingPDF ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generando...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Descargar PDF
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs de navegación */}
      <Tabs value={activeTab} onValueChange={(value) => {
        setActiveTab(value)
        if (value === "growth") {
          loadGrowthCharts()
        }
      }} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="results">Resultados</TabsTrigger>
          <TabsTrigger value="anemia">Estado Anémico</TabsTrigger>
          <TabsTrigger value="nutrition">Recomendaciones Nutricionales</TabsTrigger>
          <TabsTrigger value="growth">Curvas de Crecimiento</TabsTrigger>
        </TabsList>

        <TabsContent value="results" className="space-y-6">
          {/* 1. ANÁLISIS ANTROPOMÉTRICO COMPLETO */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Activity className="w-6 h-6 text-blue-500" />
                Análisis Antropométrico
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 bg-white rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <Scale className="w-5 h-5 text-blue-500" />
                    <span className="font-semibold text-slate-700">Peso</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">{followUpData.weight} kg</div>
                  {assessmentData?.weight_info && (
                    <div className="text-xs text-slate-500 mt-1">
                      Peso esperado: {assessmentData.weight_info.expected_weight?.toFixed(1)} kg
                    </div>
                  )}
                </div>

                <div className="p-4 bg-white rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <Ruler className="w-5 h-5 text-blue-500" />
                    <span className="font-semibold text-slate-700">Estatura</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">{followUpData.height} cm</div>
                </div>

                <div className="p-4 bg-white rounded-lg border">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    <span className="font-semibold text-slate-700">IMC</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">
                    {assessmentData?.assessment.bmi?.toFixed(1) || 'N/A'}
                  </div>
                </div>

                {followUpData.headCircumference && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="font-semibold text-slate-700 mb-2">Perímetro Cefálico</div>
                    <div className="text-2xl font-bold text-blue-600">{followUpData.headCircumference} cm</div>
                  </div>
                )}

                {followUpData.armCircumference && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="font-semibold text-slate-700 mb-2">Circunferencia Braquial</div>
                    <div className="text-2xl font-bold text-blue-600">{followUpData.armCircumference} cm</div>
                  </div>
                )}

                {followUpData.tricepsFold && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="font-semibold text-slate-700 mb-2">Pliegue Tricipital</div>
                    <div className="text-2xl font-bold text-blue-600">{followUpData.tricepsFold} mm</div>
                  </div>
                )}

                {followUpData.subscapularFold && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="font-semibold text-slate-700 mb-2">Pliegue Subescapular</div>
                    <div className="text-2xl font-bold text-blue-600">{followUpData.subscapularFold} mm</div>
                  </div>
                )}

                {followUpData.abdominalPerimeter && (
                  <div className="p-4 bg-white rounded-lg border">
                    <div className="font-semibold text-slate-700 mb-2">Perímetro Abdominal</div>
                    <div className="text-2xl font-bold text-blue-600">{followUpData.abdominalPerimeter} cm</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 2. TABLA DE CLASIFICACIÓN NUTRICIONAL */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800">Clasificación Nutricional</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-slate-700 text-white">
                      <th className="p-3 text-left border">Indicador (Z-score)</th>
                      <th className="p-3 text-center border">Valor</th>
                      <th className="p-3 text-center border">Rango de referencia (normal)</th>
                      <th className="p-3 text-left border">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white">
                    <tr>
                      <td className="p-3 border font-semibold">Peso para la Edad</td>
                      <td className="p-3 border text-center">
                        {assessmentData?.assessment.weight_for_age_zscore?.toFixed(2) || 'N/A'}
                      </td>
                      <td className="p-3 border text-center">{getRangoReferencia('peso_edad')}</td>
                      <td className={`p-3 border ${getStatusColor(nutritionalStatus.peso_edad)}`}>
                        {nutritionalStatus.peso_edad || 'N/A'}
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3 border font-semibold">Talla para la Edad</td>
                      <td className="p-3 border text-center">
                        {assessmentData?.assessment.height_for_age_zscore?.toFixed(2) || 'N/A'}
                      </td>
                      <td className="p-3 border text-center">{getRangoReferencia('talla_edad')}</td>
                      <td className={`p-3 border ${getStatusColor(nutritionalStatus.talla_edad)}`}>
                        {nutritionalStatus.talla_edad || 'N/A'}
                      </td>
                    </tr>
                    <tr>
                      <td className="p-3 border font-semibold">IMC para la Edad</td>
                      <td className="p-3 border text-center">
                        {assessmentData?.assessment.bmi_for_age_zscore?.toFixed(2) || 'N/A'}
                      </td>
                      <td className="p-3 border text-center">{getRangoReferencia('imc_edad')}</td>
                      <td className={`p-3 border ${getStatusColor(nutritionalStatus.imc_edad)}`}>
                        {nutritionalStatus.imc_edad || 'N/A'}
                      </td>
                    </tr>

                    {assessmentData?.assessment.head_circumference_zscore && (
                      <tr>
                        <td className="p-3 border font-semibold">Circunferencia craneal</td>
                        <td className="p-3 border text-center">
                          {assessmentData.assessment.head_circumference_zscore.toFixed(2)}
                        </td>
                        <td className="p-3 border text-center">{getRangoReferencia('perimetro_cefalico_edad')}</td>
                        <td className={`p-3 border ${getStatusColor(assessmentData?.assessment.nutritional_status.perimetro_cefalico_edad || '')}`}>
                          {assessmentData?.assessment.nutritional_status.perimetro_cefalico_edad || 'N/A'}
                        </td>
                      </tr>
                    )}
                    {assessmentData?.assessment.triceps_skinfold_zscore && (
                      <tr>
                        <td className="p-3 border font-semibold">Pliegue triceps</td>
                        <td className="p-3 border text-center">
                          {assessmentData.assessment.triceps_skinfold_zscore === -Infinity 
                            ? '-inf' 
                            : assessmentData.assessment.triceps_skinfold_zscore.toFixed(2)}
                        </td>
                        <td className="p-3 border text-center">{getRangoReferencia('pliegue_triceps')}</td>
                        <td className={`p-3 border ${getStatusColor(assessmentData?.assessment.nutritional_status.pliegue_triceps || '')}`}>
                          {assessmentData?.assessment.nutritional_status.pliegue_triceps || 'N/A'}
                        </td>
                      </tr>
                    )}
                    {assessmentData?.assessment.subscapular_skinfold_zscore && (
                      <tr>
                        <td className="p-3 border font-semibold">Pliegue subescapular</td>
                        <td className="p-3 border text-center">
                          {assessmentData.assessment.subscapular_skinfold_zscore === -Infinity 
                            ? '-inf' 
                            : assessmentData.assessment.subscapular_skinfold_zscore.toFixed(2)}
                        </td>
                        <td className="p-3 border text-center">{getRangoReferencia('pliegue_subescapular')}</td>
                        <td className={`p-3 border ${getStatusColor(assessmentData?.assessment.nutritional_status.pliegue_subescapular || '')}`}>
                          {assessmentData?.assessment.nutritional_status.pliegue_subescapular || 'N/A'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* 3. OBSERVACIONES CLÍNICAS */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-amber-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <FileText className="w-6 h-6 text-amber-500" />
                Observaciones Clínicas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Síntomas */}
              <div className="bg-white p-4 rounded-lg border border-amber-200">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600" />
                  <h4 className="font-bold text-slate-800 text-base">Síntomas reportados</h4>
                </div>
                {followUpData.symptoms && followUpData.symptoms.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {followUpData.symptoms.map((symptom: string, idx: number) => (
                      <Badge key={idx} variant="outline" className="bg-amber-50 text-amber-700 border-amber-300">
                        {symptom}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm italic">No se reportaron síntomas</p>
                )}
              </div>

              {/* Signos físicos */}
              {followUpData.physicalSigns && followUpData.physicalSigns.length > 0 && (
                <div className="bg-white p-4 rounded-lg border border-red-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Activity className="w-5 h-5 text-red-600" />
                    <h4 className="font-bold text-slate-800 text-base">Signos físicos observados</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {followUpData.physicalSigns.map((sign: string, idx: number) => (
                      <Badge key={idx} variant="outline" className="bg-red-50 text-red-700 border-red-300">
                        {sign}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Observación del nutricionista */}
              <div className="bg-white p-4 rounded-lg border border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <User className="w-5 h-5 text-blue-600" />
                  <h4 className="font-bold text-slate-800 text-base">Observación del nutricionista</h4>
                </div>
                {followUpData.clinicalObservations ? (
                  <div className="bg-blue-50 p-3 rounded border border-blue-100">
                    <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap">
                      {followUpData.clinicalObservations}
                    </p>
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm italic">Sin observaciones adicionales del nutricionista</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="anemia" className="space-y-6">
          {(() => {
            const anemiaResultStr = sessionStorage.getItem('anemia_result')
            const anemiaResult = anemiaResultStr ? JSON.parse(anemiaResultStr) : null
            
            if (!anemiaResult) {
              return (
                <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-amber-50`}>
                  <CardContent className="p-8">
                    <div className="text-center space-y-3">
                      <AlertCircle className="w-12 h-12 text-amber-500 mx-auto" />
                      <h3 className="text-lg font-semibold text-slate-800">Sin información de anemia</h3>
                      <p className="text-slate-600">
                        No se han proporcionado datos de hemoglobina ni fotografía de ojos para evaluar anemia.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )
            }
            
            return (
              <Card className={`${theme.cardBorder} bg-gradient-to-br ${
                anemiaResult.isAnemic 
                  ? 'from-red-50 to-orange-50 border-red-300' 
                  : 'from-green-50 to-emerald-50 border-green-300'
              }`}>
                <CardHeader>
                  <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <Activity className="w-6 h-6" />
                    Evaluación de Anemia
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Estado de anemia */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="border-2 shadow-sm">
                      <CardContent className="p-6">
                        <div className="text-center space-y-2">
                          <div className="text-sm text-slate-600 font-medium">Fuente de datos</div>
                          <Badge className="bg-blue-100 text-blue-800 text-sm py-1">
                            {anemiaResult.source === 'hemoglobina' 
                              ? 'Examen de sangre' 
                              : 'Análisis de imagen'}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card className="border-2 shadow-sm">
                      <CardContent className="p-6">
                        <div className="text-center space-y-2">
                          <div className="text-sm text-slate-600 font-medium">Hemoglobina estimada</div>
                          <div className="text-3xl font-bold text-slate-800">
                            {anemiaResult.value.toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-600">g/dL</div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card className="border-2 shadow-sm">
                      <CardContent className="p-6">
                        <div className="text-center space-y-2">
                          <div className="text-sm text-slate-600 font-medium">Umbral OMS</div>
                          <div className="text-3xl font-bold text-slate-800">
                            {anemiaResult.threshold.toFixed(2)}
                          </div>
                          <div className="text-xs text-slate-600">g/dL</div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Resultado principal */}
                  <div className={`p-6 rounded-lg border-2 ${
                    anemiaResult.isAnemic
                      ? 'bg-red-100 border-red-400'
                      : 'bg-green-100 border-green-400'
                  }`}>
                    <div className="flex items-center gap-4">
                      {anemiaResult.isAnemic ? (
                        <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0" />
                      ) : (
                        <CheckCircle className="w-8 h-8 text-green-600 flex-shrink-0" />
                      )}
                      <div>
                        <h3 className={`text-xl font-bold ${
                          anemiaResult.isAnemic ? 'text-red-700' : 'text-green-700'
                        }`}>
                          {anemiaResult.label}
                        </h3>
                        <p className={`text-sm ${
                          anemiaResult.isAnemic ? 'text-red-600' : 'text-green-600'
                        }`}>
                          Hemoglobina {anemiaResult.isAnemic ? 'por debajo' : 'dentro'} del umbral normal
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Recomendaciones */}
                  <Card className="bg-white border">
                    <CardHeader>
                      <CardTitle className="text-base font-semibold text-slate-800">Recomendaciones</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {anemiaResult.isAnemic && (
                        <div className="space-y-2">
                          <div className="flex gap-3">
                            <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="font-semibold text-slate-800">Se recomienda realizar un examen de sangre</p>
                              <p className="text-sm text-slate-600 mt-1">
                                Para confirmar anemia y determinar su causa (deficiencia de hierro, vitamina B12, etc.)
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <div className="space-y-2">
                        <div className="flex gap-3">
                          <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="font-semibold text-slate-800">Recomendaciones nutricionales</p>
                            <p className="text-sm text-slate-600 mt-1">
                              Aumentar ingesta de alimentos ricos en hierro, ácido fólico y vitamina B12:
                            </p>
                            <ul className="text-sm text-slate-600 mt-2 ml-4 list-disc space-y-1">
                              <li>Carnes rojas magras</li>
                              <li>Hígado y otras vísceras</li>
                              <li>Huevos</li>
                              <li>Legumbres (lentejas, frijoles)</li>
                              <li>Frutas cítricas (vitamina C para mejor absorción)</li>
                            </ul>
                          </div>
                        </div>
                      </div>

                      {anemiaResult.source === 'modelo' && (
                        <div className="space-y-2 mt-4 pt-4 border-t">
                          <div className="flex gap-3">
                            <FileText className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                            <div>
                              <p className="font-semibold text-slate-800">Nota importante</p>
                              <p className="text-sm text-slate-600 mt-1">
                                Este resultado es una estimación basada en análisis de imagen. 
                                {anemiaResult.isAnemic 
                                  ? ' Se recomienda confirmar con un examen de sangre.'
                                  : ' Se recomienda confirmar con un examen de sangre si hay síntomas.'}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Parámetros técnicos (si es del modelo) */}
                  {anemiaResult.source === 'modelo' && (
                    <Card className="bg-slate-50 border">
                      <CardHeader>
                        <CardTitle className="text-base font-semibold text-slate-800">Parámetros de análisis</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-slate-600">Diferencia vs. umbral:</p>
                            <p className={`font-semibold ${
                              anemiaResult.isAnemic ? 'text-red-600' : 'text-green-600'
                            }`}>
                              {(anemiaResult.value - anemiaResult.threshold).toFixed(2)} g/dL
                            </p>
                          </div>
                          <div>
                            <p className="text-slate-600">Método:</p>
                            <p className="font-semibold text-slate-800">Análisis digital de imagen</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </CardContent>
              </Card>
            )
          })()}
        </TabsContent>

        <TabsContent value="nutrition" className="space-y-6">
          {/* 1. REQUERIMIENTOS ENERGÉTICOS */}
          {assessmentData?.energy_requirements && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Requerimientos Energéticos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-white rounded-lg border">
                    <div className="text-3xl font-bold text-purple-600">
                      {assessmentData.energy_requirements.kcal_per_day?.toFixed(0) || 'N/A'}
                    </div>
                    <div className="text-sm text-slate-600">kcal/día</div>
                    {assessmentData.weight_info && (
                      <div className="text-xs text-slate-500 mt-2">
                        Para peso esperado: {assessmentData.weight_info.expected_weight?.toFixed(1)} kg
                      </div>
                    )}
                  </div>
                  {assessmentData.energy_requirements.kcal_per_kg && (
                    <div className="text-center p-4 bg-white rounded-lg border">
                      <div className="text-3xl font-bold text-purple-600">
                        {assessmentData.energy_requirements.kcal_per_kg?.toFixed(1)}
                      </div>
                      <div className="text-sm text-slate-600">kcal/kg/día</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* 2. REQUERIMIENTOS DIARIOS DE NUTRIENTES */}
          {assessmentData?.nutrient_requirements && assessmentData.nutrient_requirements.length > 0 && (
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Requerimientos Diarios de Nutrientes</CardTitle>
              </CardHeader>
              <CardContent>
                {/* AGREGADO: contenedor con altura máxima y scroll */}
                <div className="max-h-[500px] overflow-y-auto border rounded-lg">
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse text-sm">
                      <thead className="sticky top-0 z-10">
                        <tr className="bg-slate-700 text-white">
                          <th className="p-2 text-left border">Nutriente</th>
                          <th className="p-2 text-center border">Cantidad Recomendada (g/día)</th>
                          <th className="p-2 text-left border">Alimento Sugerido</th>
                          <th className="p-2 text-center border">Cantidad en 100g</th>
                          <th className="p-2 text-center border">Cantidad Recomendada (g/día)</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white">
                        {assessmentData.nutrient_requirements.map((nutrient, idx) => {
                          const alimentos = nutrient.alimentos || []
                          const numFilas = Math.max(1, alimentos.length)
                          
                          // Limpiar el nombre del nutriente: quitar "mg/día", "g/día", "g/kg/día", asterisco, etc.
                          const nutrienteName = (nutrient.nutriente || '')
                            .replace(/\*/g, '')
                            .replace(/\s+(mg\/día|g\/kg\/día|g\/día|Aia)$/gi, '')
                            .trim()
                          
                          return alimentos.length > 0 ? (
                            alimentos.map((alimento: any[], alimentoIdx: number) => (
                              <tr key={`${idx}-${alimentoIdx}`} className={alimentoIdx % 2 === 0 ? 'bg-gray-50' : ''}>
                                {alimentoIdx === 0 && (
                                  <>
                                    <td className="p-2 border font-semibold" rowSpan={numFilas}>
                                      {nutrienteName}
                                    </td>
                                    <td className="p-2 border text-center" rowSpan={numFilas}>
                                      {nutrient.valor_recomendado || 'N/A'}
                                    </td>
                                  </>
                                )}
                                <td className="p-2 border">{alimento[0] || 'N/A'}</td>
                                <td className="p-2 border text-center">{alimento[1] || 'N/A'}</td>
                                <td className="p-2 border text-center">{alimento[2] || 'N/A'}</td>
                              </tr>
                            ))
                          ) : (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                              <td className="p-2 border font-semibold">{nutrienteName}</td>
                              <td className="p-2 border text-center">{nutrient.valor_recomendado || 'N/A'}</td>
                              <td className="p-2 border text-slate-400" colSpan={3}>Sin alimentos disponibles</td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 3. RECOMENDACIONES */}
          {assessmentData?.recommendations && (
            <>
              {assessmentData.recommendations.nutritional_recommendations?.length > 0 && (
                <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
                  <CardHeader>
                    <CardTitle className="text-xl font-bold text-slate-800">Recomendaciones Nutricionales</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {assessmentData.recommendations.nutritional_recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {assessmentData.recommendations.general_recommendations?.length > 0 && (
                <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-amber-50`}>
                  <CardHeader>
                    <CardTitle className="text-xl font-bold text-slate-800">Recomendaciones Generales</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {assessmentData.recommendations.general_recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {assessmentData.recommendations.caregiver_instructions?.length > 0 && (
                <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-pink-50`}>
                  <CardHeader>
                    <CardTitle className="text-xl font-bold text-slate-800">Instrucciones para el Cuidador</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {assessmentData.recommendations.caregiver_instructions.map((instruction, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-700">{instruction}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>

        {/* Tab 3: Curvas de Crecimiento */}
        <TabsContent value="growth" className="mt-6">
          {loadingCharts ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
                <p className="text-slate-600">Cargando curvas de crecimiento...</p>
              </div>
            </div>
          ) : Object.keys(growthCharts).length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-slate-800 mb-2">No se pudieron cargar las gráficas</h3>
                <p className="text-slate-600 mb-4">Verifica que el servidor esté funcionando correctamente</p>
                <Button onClick={loadGrowthCharts} variant="outline">
                  Reintentar
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {Object.keys(growthCharts).map(key => {
                const chartData = growthCharts[key]
                return (
                  <WHOGrowthChart key={key} data={chartData} />
                )
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}