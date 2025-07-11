"use client"

import { useState } from "react"
import { FileText, Download, Printer, Share2, AlertTriangle, CheckCircle, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import type { Child, ThemeColors } from "@/types"

interface FollowUpResultsProps {
  child: Child
  followUpData: any
  theme: ThemeColors
  onClose: () => void
  onSaveToProfile: () => void
}

interface NutritionalAssessment {
  classification: "Normal" | "Riesgo leve" | "Moderado" | "Severo"
  malnutritionType:
    | "Desnutrición aguda"
    | "Desnutrición crónica"
    | "Desnutrición mixta"
    | "Sobrepeso"
    | "Obesidad"
    | "Normal"
  clinicalSigns: string[]
  anemiaRisk: "Bajo" | "Moderado" | "Alto"
  generalStatus: "Niño aparentemente sano" | "Requiere atención" | "Posible derivación médica"
}

interface NutritionalRecommendations {
  recommendedFoods: string[]
  avoidFoods: string[]
  frequency: string
  supplements: string[]
  preparations: string[]
  additionalTips: string[]
}

interface NonDietaryRecommendations {
  hygiene: string[]
  physicalActivity: string[]
  medicalAttention: string[]
  followUp: string[]
}

export function FollowUpResults({ child, followUpData, theme, onClose, onSaveToProfile }: FollowUpResultsProps) {
  const [activeTab, setActiveTab] = useState("results")

  // Simulación de análisis automático basado en los datos del seguimiento
  const assessment: NutritionalAssessment = {
    classification: followUpData.weight < 14 ? "Moderado" : followUpData.weight > 20 ? "Riesgo leve" : "Normal",
    malnutritionType:
      followUpData.weight < 14 ? "Desnutrición aguda" : followUpData.weight > 20 ? "Sobrepeso" : "Normal",
    clinicalSigns: followUpData.physicalSigns || ["Palidez leve", "Encías normales"],
    anemiaRisk: followUpData.symptoms?.includes("Fatiga o debilidad") ? "Moderado" : "Bajo",
    generalStatus: followUpData.weight < 14 ? "Requiere atención" : "Niño aparentemente sano",
  }

  const nutritionalRecommendations: NutritionalRecommendations = {
    recommendedFoods: ["Lentejas", "Plátano verde", "Huevo", "Hígado de pollo", "Frutas locales", "Espinaca", "Quinua"],
    avoidFoods: ["Ultraprocesados", "Azúcares añadidos", "Bebidas industriales", "Comida chatarra"],
    frequency: "4 comidas principales + 2 meriendas saludables",
    supplements: assessment.anemiaRisk === "Moderado" ? ["Suplemento de hierro", "Vitamina C"] : [],
    preparations: ["Papillas espesas", "Sopas nutritivas", "Combinaciones culturales viables"],
    additionalTips: ["Aumentar consumo de agua", "Evitar picar entre comidas", "Comer en familia"],
  }

  const nonDietaryRecommendations: NonDietaryRecommendations = {
    hygiene: ["Lavado de manos antes de comer", "Higiene bucal después de comidas", "Agua hervida o filtrada"],
    physicalActivity: ["Juego activo supervisado", "Evitar sedentarismo excesivo", "Actividades al aire libre"],
    medicalAttention:
      assessment.classification === "Moderado" ? ["Requiere valoración médica por signos de desnutrición"] : [],
    followUp:
      assessment.classification === "Moderado" ? ["Próximo control en 2 semanas"] : ["Monitorear evolución en 1 mes"],
  }

  const caregiverInstructions = `Su hijo ${child.name} ${
    assessment.classification === "Normal"
      ? "presenta un estado nutricional adecuado. Continue con los buenos hábitos alimentarios."
      : "necesita mejorar su alimentación. Le recomendamos ofrecerle más alimentos ricos en hierro como lentejas, carne, espinaca y jugos de frutas naturales. Intente que coma 5 veces al día y evite los dulces entre comidas."
  }`

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case "Normal":
        return "bg-green-100 text-green-800"
      case "Riesgo leve":
        return "bg-yellow-100 text-yellow-800"
      case "Moderado":
        return "bg-orange-100 text-orange-800"
      case "Severo":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const generatePDF = (type: "clinical" | "caregiver") => {
    alert(`Generando reporte ${type === "clinical" ? "clínico" : "para el cuidador"}...`)
  }

  const handleSave = () => {
    onSaveToProfile()
    alert("Resultados guardados en el perfil del niño exitosamente")
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
          {/* Clasificación nutricional */}
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
                    <span className="font-medium text-slate-700">Estado Nutricional:</span>
                    <Badge className={getClassificationColor(assessment.classification)}>
                      {assessment.classification}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Tipo de Malnutrición:</span>
                    <Badge variant="outline">{assessment.malnutritionType}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Riesgo de Anemia:</span>
                    <Badge
                      className={
                        assessment.anemiaRisk === "Alto"
                          ? "bg-red-100 text-red-800"
                          : assessment.anemiaRisk === "Moderado"
                            ? "bg-orange-100 text-orange-800"
                            : "bg-green-100 text-green-800"
                      }
                    >
                      {assessment.anemiaRisk}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-slate-700">Estado General:</span>
                    <p className="text-sm text-slate-600 mt-1">{assessment.generalStatus}</p>
                  </div>
                  <div>
                    <span className="font-medium text-slate-700">Signos Clínicos:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {assessment.clinicalSigns.map((sign, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {sign}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Datos antropométricos calculados */}
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
                    {followUpData.weight && followUpData.height
                      ? (
                          Number.parseFloat(followUpData.weight) /
                          Math.pow(Number.parseFloat(followUpData.height) / 100, 2)
                        ).toFixed(1)
                      : "N/A"}
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
        </TabsContent>

        <TabsContent value="nutrition" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Alimentos recomendados */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Alimentos Recomendados</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nutritionalRecommendations.recommendedFoods.map((food, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-slate-700">{food}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Alimentos a evitar */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-red-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Alimentos a Evitar</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nutritionalRecommendations.avoidFoods.map((food, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                      <span className="text-sm text-slate-700">{food}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Frecuencia y suplementos */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Frecuencia y Suplementos</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-slate-700 mb-2">Frecuencia Sugerida:</h4>
                  <p className="text-sm text-slate-600">{nutritionalRecommendations.frequency}</p>
                </div>
                {nutritionalRecommendations.supplements.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-slate-700 mb-2">Suplementos:</h4>
                    <div className="space-y-1">
                      {nutritionalRecommendations.supplements.map((supplement, index) => (
                        <Badge key={index} variant="outline" className="mr-2">
                          {supplement}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Preparaciones */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Preparaciones Sugeridas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {nutritionalRecommendations.preparations.map((prep, index) => (
                    <div key={index} className="text-sm text-slate-700">
                      • {prep}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Consejos adicionales */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-orange-50`}>
            <CardHeader>
              <CardTitle className="text-lg font-bold text-slate-800">Consejos Adicionales</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {nutritionalRecommendations.additionalTips.map((tip, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-orange-500" />
                    <span className="text-sm text-slate-700">{tip}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="general" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Higiene */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Higiene</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nonDietaryRecommendations.hygiene.map((item, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-blue-500" />
                      <span className="text-sm text-slate-700">{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Actividad física */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Actividad Física</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nonDietaryRecommendations.physicalActivity.map((item, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-slate-700">{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Atención médica */}
            {nonDietaryRecommendations.medicalAttention.length > 0 && (
              <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-red-50`}>
                <CardHeader>
                  <CardTitle className="text-lg font-bold text-slate-800">Atención Médica</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {nonDietaryRecommendations.medicalAttention.map((item, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-red-500" />
                        <span className="text-sm text-slate-700">{item}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Seguimiento */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Seguimiento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {nonDietaryRecommendations.followUp.map((item, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-purple-500" />
                      <span className="text-sm text-slate-700">{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="caregiver" className="space-y-6">
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-yellow-50`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <User className="w-5 h-5" />
                Indicaciones para el Cuidador
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-white p-6 rounded-lg border border-yellow-200">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Resumen para {child.guardian}</h3>
                <p className="text-slate-700 leading-relaxed text-base">{caregiverInstructions}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold text-slate-800 mb-3">✅ Alimentos Buenos</h4>
                  <ul className="space-y-1 text-sm text-slate-600">
                    {nutritionalRecommendations.recommendedFoods.slice(0, 5).map((food, index) => (
                      <li key={index}>• {food}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-white p-4 rounded-lg border">
                  <h4 className="font-semibold text-slate-800 mb-3">❌ Alimentos a Evitar</h4>
                  <ul className="space-y-1 text-sm text-slate-600">
                    {nutritionalRecommendations.avoidFoods.map((food, index) => (
                      <li key={index}>• {food}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-semibold text-slate-800 mb-3">📅 Próxima Cita</h4>
                <p className="text-slate-700">{nonDietaryRecommendations.followUp[0]}</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Botones de acción */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4 justify-center">
            <Button
              onClick={() => generatePDF("clinical")}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white"
            >
              <FileText className="w-4 h-4 mr-2" />
              Reporte Clínico PDF
            </Button>
            <Button
              onClick={() => generatePDF("caregiver")}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Reporte para Cuidador
            </Button>
            <Button variant="outline" className="border-purple-200 text-purple-600 hover:bg-purple-50 bg-transparent">
              <Printer className="w-4 h-4 mr-2" />
              Imprimir
            </Button>
            <Button variant="outline" className="border-orange-200 text-orange-600 hover:bg-orange-50 bg-transparent">
              <Share2 className="w-4 h-4 mr-2" />
              Compartir
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
