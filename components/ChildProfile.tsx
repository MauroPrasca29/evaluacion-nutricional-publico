"use client"
import { useState } from "react"
import { ArrowLeft, User, FileText, TrendingUp, Calendar, Phone, Weight, Stethoscope, ClipboardList, AlertTriangle, Download, HeartPulse, Apple, Bike } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { GrowthChart } from "@/components/GrowthChart"
import type { Child, MedicalRecord, ThemeColors } from "@/types"

interface ChildProfileProps {
  child: Child
  theme: ThemeColors
  onBack: () => void
}

const StatusBadge = ({ status }: { status: MedicalRecord["nutritionalStatus"] }) => {
  const statusStyles = {
    normal: "bg-green-100 text-green-800",
    riesgo: "bg-yellow-100 text-yellow-800",
    seguimiento: "bg-blue-100 text-blue-800",
    alerta: "bg-orange-100 text-orange-800",
    severo: "bg-red-100 text-red-800",
  }
  return <Badge className={`${statusStyles[status]} capitalize`}>{status}</Badge>
}

export function ChildProfile({ child, theme, onBack }: ChildProfileProps) {
  const [activeTab, setActiveTab] = useState("historial")

  const calculateAge = (birthDate: string) => {
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const m = today.getMonth() - birth.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age
  }

  const calculateBMI = (weight: number, height: number) => {
    if (height === 0) return "N/A"
    const heightInMeters = height / 100
    return (weight / (heightInMeters * heightInMeters)).toFixed(1)
  }

  return (
    <div className="space-y-6">
      {/* Header del perfil */}
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          onClick={onBack}
          className={`${theme.cardBorder} hover:bg-opacity-50 transition-all duration-300 hover:scale-105`}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver
        </Button>
        <div className="flex items-center gap-4">
          <Avatar className="w-16 h-16">
            <AvatarFallback
              className={`bg-gradient-to-br ${theme.buttonColor.split(" ")[0]} text-white font-bold text-lg`}
            >
              {child.name
                .split(" ")
                .map((n) => n[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">{child.name}</h1>
            <p className="text-slate-600 text-lg">
              {calculateAge(child.birthDate)} años • ID: {child.id} • {child.community}
            </p>
            <Badge
              className={`mt-2 ${
                child.status === "normal" ? "bg-green-100 text-green-800" : "bg-orange-100 text-orange-800"
              }`}
            >
              Estado General: {child.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Tabs del perfil */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="historial" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Historial Clínico
          </TabsTrigger>
          <TabsTrigger value="crecimiento" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Crecimiento
          </TabsTrigger>
          <TabsTrigger value="reportes" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Reportes
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Información Personal */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Información Personal
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-600">Fecha de Nacimiento:</span>
                  <span className="font-bold text-slate-800">{child.birthDate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Género:</span>
                  <span className="font-bold text-slate-800 capitalize">{child.gender}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Comunidad:</span>
                  <span className="font-bold text-slate-800">{child.community}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Última visita:</span>
                  <span className="font-bold text-slate-800">{child.lastVisit}</span>
                </div>
              </CardContent>
            </Card>

            {/* Información del Acudiente */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  Acudiente
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-600">Nombre:</span>
                  <span className="font-bold text-slate-800">{child.guardian}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Teléfono:</span>
                  <span className="font-bold text-slate-800">{child.phone}</span>
                </div>
                <div className="flex justify-between items-start">
                  <span className="text-slate-600">Dirección:</span>
                  <span className="font-bold text-slate-800 text-right">{child.address}</span>
                </div>
              </CardContent>
            </Card>

            {/* Mediciones Actuales */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                  <Weight className="w-5 h-5" />
                  Mediciones Actuales
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-600">Peso:</span>
                  <span className="font-bold text-slate-800">{child.weight} kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Talla:</span>
                  <span className="font-bold text-slate-800">{child.height} cm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">IMC:</span>
                  <span className="font-bold text-slate-800">{calculateBMI(child.weight, child.height)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="historial" className="space-y-6 mt-6">
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-3">
                <HeartPulse className="w-6 h-6 text-blue-500" />
                Historial de Consultas
              </CardTitle>
            </CardHeader>
            <CardContent>
              {child.medicalHistory.length > 0 ? (
                <Accordion type="single" collapsible className="w-full">
                  {child.medicalHistory.map((record) => (
                    <AccordionItem value={`item-${record.id}`} key={record.id}>
                      <AccordionTrigger className="hover:bg-slate-50 -mx-4 px-4 rounded-md">
                        <div className="flex justify-between items-center w-full">
                          <div className="flex items-center gap-4">
                            <Calendar className="w-5 h-5 text-slate-500" />
                            <span className="font-bold text-slate-700 text-lg">{record.date}</span>
                          </div>
                          <div className="flex items-center gap-4">
                            <StatusBadge status={record.nutritionalStatus} />
                            <span className="text-sm text-slate-500 hidden md:block">
                              Atendido por: {record.professional}
                            </span>
                          </div>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="pt-4 pb-2 space-y-6">
                        {record.alerts.length > 0 && (
                          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                            <h4 className="font-bold text-red-800 flex items-center gap-2 mb-2">
                              <AlertTriangle className="w-5 h-5" />
                              Alertas Detectadas
                            </h4>
                            <ul className="list-disc list-inside text-red-700 space-y-1">
                              {record.alerts.map((alert, i) => (<li key={i}>{alert}</li>))}
                            </ul>
                          </div>
                        )}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <h4 className="font-bold text-slate-700 flex items-center gap-2">
                              <Stethoscope className="w-5 h-5 text-blue-500" />
                              Datos de la Consulta
                            </h4>
                            <div className="text-sm space-y-2 pl-7">
                              <p><strong>Peso:</strong> {record.weight} kg</p>
                              <p><strong>Talla:</strong> {record.height} cm</p>
                              <p><strong>IMC:</strong> {record.bmi}</p>
                              <p><strong>Vacunas aplicadas:</strong> {record.vaccinations.length > 0 ? record.vaccinations.join(", ") : "Ninguna"}</p>
                            </div>
                          </div>
                          <div className="space-y-4">
                            <h4 className="font-bold text-slate-700 flex items-center gap-2">
                              <ClipboardList className="w-5 h-5 text-blue-500" />
                              Observaciones Clínicas
                            </h4>
                            <p className="text-sm text-slate-600 pl-7">{record.observations}</p>
                          </div>
                        </div>
                        <div className="space-y-4">
                          <h4 className="font-bold text-slate-700 flex items-center gap-2">
                            <ClipboardList className="w-5 h-5 text-blue-500" />
                            Recomendaciones
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pl-7">
                            <div className="space-y-2">
                              <h5 className="font-semibold flex items-center gap-2"><Apple className="w-4 h-4 text-green-600" /> Nutricionales</h5>
                              <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                {record.recommendations.dietary.map((rec, i) => (<li key={i}>{rec}</li>))}
                              </ul>
                            </div>
                            <div className="space-y-2">
                              <h5 className="font-semibold flex items-center gap-2"><Bike className="w-4 h-4 text-orange-600" /> Generales</h5>
                              <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
                                {record.recommendations.general.map((rec, i) => (<li key={i}>{rec}</li>))}
                              </ul>
                            </div>
                          </div>
                        </div>
                        <div className="flex justify-end pt-4">
                          <Button variant="outline" size="sm"><Download className="w-4 h-4 mr-2" />Descargar Reporte ({record.reportId})</Button>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <div className="text-center py-10">
                  <p className="text-slate-600">No hay registros médicos disponibles para este niño.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="crecimiento" className="space-y-6 mt-6">
          <GrowthChart growthHistory={child.growthHistory} theme={theme} />
        </TabsContent>

        <TabsContent value="reportes" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
              <CardHeader><CardTitle className="text-lg font-bold text-slate-800">Generar Reportes</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Button variant="outline" className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}><FileText className="w-4 h-4 mr-2" />Reporte Individual PDF</Button>
                <Button variant="outline" className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}><TrendingUp className="w-4 h-4 mr-2" />Gráfico de Crecimiento</Button>
              </CardContent>
            </Card>
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader><CardTitle className="text-lg font-bold text-slate-800">Estadísticas</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between"><span className="text-slate-600">Total de consultas:</span><span className="font-bold text-slate-800">{child.medicalHistory.length}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Registros de crecimiento:</span><span className="font-bold text-slate-800">{child.growthHistory.length}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">Estado actual:</span><Badge className={`${child.status === "normal" ? "bg-green-100 text-green-800" : "bg-orange-100 text-orange-800"}`}>{child.status}</Badge></div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
