// components/ChildProfile.tsx

"use client"
import { useState, useEffect } from "react"
import { ArrowLeft, User, FileText, TrendingUp, Calendar, Phone, Weight, Stethoscope, ClipboardList, AlertTriangle, Download, HeartPulse, Apple, Bike, Loader2 } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { GrowthChart } from "@/components/GrowthChart"
import { FollowUpResults } from "@/components/FollowUpResults"
import type { Child, ThemeColors, FollowUpForm } from "@/types"

interface ChildProfileProps {
  child: Child
  theme: ThemeColors
  onBack: () => void
}

interface Seguimiento {
  id_seguimiento: number
  fecha: string
  observacion: string | null
  encargado_id: number | null
  peso?: number
  estatura?: number
  imc?: number
}

interface SedeData {
  id_sede: number
  nombre: string
  municipio: string | null
  departamento: string | null
}

interface AcudienteData {
  id_acudiente: number
  nombre: string
  telefono: string | null
  correo: string | null
  direccion: string | null
}

interface SelectedSeguimiento {
  child: Child
  followUpData: FollowUpForm
  seguimientoId: number
}

export function ChildProfile({ child, theme, onBack }: ChildProfileProps) {
  const [activeTab, setActiveTab] = useState("general")
  const [seguimientos, setSeguimientos] = useState<Seguimiento[]>([])
  const [sede, setSede] = useState<SedeData | null>(null)
  const [acudiente, setAcudiente] = useState<AcudienteData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedSeguimiento, setSelectedSeguimiento] = useState<SelectedSeguimiento | null>(null)

  useEffect(() => {
    const loadChildData = async () => {
      setLoading(true)
      try {
        // Cargar seguimientos del infante
        const followupsRes = await fetch(`/api/children/${child.id}/followups`)
        if (followupsRes.ok) {
          const data = await followupsRes.json()
          console.log("Seguimientos recibidos:", data)
          setSeguimientos(data)
        } else {
          console.error("Error al cargar seguimientos:", followupsRes.status)
        }

        // Cargar información de sede si existe
        if (child.community && child.community !== "N/A") {
          const sedeId = parseInt(child.community)
          if (!isNaN(sedeId)) {
            const sedeRes = await fetch(`/api/sedes/${sedeId}`)
            if (sedeRes.ok) {
              const sedeData = await sedeRes.json()
              setSede(sedeData)
            }
          }
        }

        // Cargar información de acudiente si existe
        if (child.guardian && child.guardian !== "N/A") {
          const acudienteId = parseInt(child.guardian)
          if (!isNaN(acudienteId)) {
            const acudienteRes = await fetch(`/api/acudientes/${acudienteId}`)
            if (acudienteRes.ok) {
              const acudienteData = await acudienteRes.json()
              setAcudiente(acudienteData)
            }
          }
        }
      } catch (error) {
        console.error("Error cargando datos del perfil:", error)
      } finally {
        setLoading(false)
      }
    }

    loadChildData()
  }, [child.id, child.community, child.guardian])

  // Si hay un seguimiento seleccionado, mostrar los resultados
  if (selectedSeguimiento) {
    return (
      <FollowUpResults
        child={selectedSeguimiento.child}
        followUpData={selectedSeguimiento.followUpData}
        theme={theme}
        onClose={() => setSelectedSeguimiento(null)}
        onSaveToProfile={() => {
          setSelectedSeguimiento(null)
        }}
      />
    )
  }

  const calculateAge = (birthDate: string) => {
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const m = today.getMonth() - birth.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    
    if (age === 0) {
      const months = m < 0 ? 12 + m : m
      return `${months} mes${months !== 1 ? 'es' : ''}`
    }
    
    return `${age} año${age !== 1 ? 's' : ''}`
  }

  const calculateBMI = (weight: number, height: number) => {
    if (!height || height === 0) return "N/A"
    const heightInMeters = height / 100
    return (weight / (heightInMeters * heightInMeters)).toFixed(1)
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-CO', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  const getLatestMeasurements = () => {
    if (seguimientos.length === 0) {
      return { peso: 0, estatura: 0, imc: 0 }
    }
    
    console.log("Calculando última medición de:", seguimientos) // DEBUG
    
    // El backend ya envía ordenado por fecha descendente
    // Tomamos el primer elemento que es el más reciente
    const latest = seguimientos[0]
    
    console.log("Seguimiento más reciente:", latest) // DEBUG
    
    return {
      peso: latest.peso || 0,
      estatura: latest.estatura || 0,
      imc: latest.imc || (latest.peso && latest.estatura ? parseFloat(calculateBMI(latest.peso, latest.estatura)) : 0)
    }
  }

  const measurements = getLatestMeasurements()

  // Convertir seguimientos a formato de historial de crecimiento para GrowthChart
  const growthHistory = seguimientos
    .filter(s => s.peso && s.estatura)
    .map(s => ({
      date: formatDate(s.fecha),
      weight: s.peso || 0,
      height: s.estatura || 0,
      bmi: s.imc || parseFloat(calculateBMI(s.peso || 0, s.estatura || 0))
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()) // Orden ascendente para el gráfico

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
              {calculateAge(child.birthDate)} • {sede?.nombre || child.community}
            </p>
            <Badge className="mt-2 bg-blue-100 text-blue-800">
              {seguimientos.length} seguimiento{seguimientos.length !== 1 ? 's' : ''} registrado{seguimientos.length !== 1 ? 's' : ''}
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
            Historial
          </TabsTrigger>
          <TabsTrigger value="crecimiento" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Crecimiento
          </TabsTrigger>
          <TabsTrigger value="reportes" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Estadísticas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6 mt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
              <span className="ml-3 text-slate-600">Cargando información...</span>
            </div>
          ) : (
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
                    <span className="font-bold text-slate-800">{formatDate(child.birthDate)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Género:</span>
                    <span className="font-bold text-slate-800 capitalize">{child.gender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Edad:</span>
                    <span className="font-bold text-slate-800">{calculateAge(child.birthDate)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Sede:</span>
                    <span className="font-bold text-slate-800">{sede?.nombre || "Sin sede"}</span>
                  </div>
                  {sede?.municipio && (
                    <div className="flex justify-between">
                      <span className="text-slate-600">Municipio:</span>
                      <span className="font-bold text-slate-800">{sede.municipio}</span>
                    </div>
                  )}
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
                  {acudiente ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Nombre:</span>
                        <span className="font-bold text-slate-800">{acudiente.nombre}</span>
                      </div>
                      {acudiente.telefono && (
                        <div className="flex justify-between">
                          <span className="text-slate-600">Teléfono:</span>
                          <span className="font-bold text-slate-800">{acudiente.telefono}</span>
                        </div>
                      )}
                      {acudiente.correo && (
                        <div className="flex justify-between">
                          <span className="text-slate-600">Correo:</span>
                          <span className="font-bold text-slate-800 text-sm">{acudiente.correo}</span>
                        </div>
                      )}
                      {acudiente.direccion && (
                        <div className="flex justify-between items-start">
                          <span className="text-slate-600">Dirección:</span>
                          <span className="font-bold text-slate-800 text-right text-sm">{acudiente.direccion}</span>
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="text-slate-500 text-center py-4">Sin acudiente registrado</p>
                  )}
                </CardContent>
              </Card>

              {/* Mediciones Actuales */}
              <Card
                className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}
              >
                <CardHeader>
                  <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <Weight className="w-5 h-5" />
                    Última Medición
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {measurements.peso > 0 ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Peso:</span>
                        <span className="font-bold text-slate-800">{measurements.peso} kg</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Talla:</span>
                        <span className="font-bold text-slate-800">{measurements.estatura} cm</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">IMC:</span>
                        <span className="font-bold text-slate-800">{measurements.imc.toFixed(1)}</span>
                      </div>
                    </>
                  ) : (
                    <p className="text-slate-500 text-center py-4">Sin mediciones registradas</p>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="historial" className="space-y-6 mt-6">
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-3">
                <HeartPulse className="w-6 h-6 text-blue-500" />
                Historial de Seguimientos
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-amber-600" />
                </div>
              ) : seguimientos.length > 0 ? (
                <Accordion type="single" collapsible className="w-full">
                  {seguimientos.map((seguimiento) => (
                    <AccordionItem value={`item-${seguimiento.id_seguimiento}`} key={seguimiento.id_seguimiento}>
                      <AccordionTrigger className="hover:bg-slate-50 -mx-4 px-4 rounded-md">
                        <div className="flex justify-between items-center w-full">
                          <div className="flex items-center gap-4">
                            <Calendar className="w-5 h-5 text-slate-500" />
                            <span className="font-bold text-slate-700 text-lg">{formatDate(seguimiento.fecha)}</span>
                          </div>
                          {seguimiento.peso && (
                            <Badge className="bg-green-100 text-green-800">
                              {seguimiento.peso} kg • {seguimiento.estatura} cm
                            </Badge>
                          )}
                        </div>
                      </AccordionTrigger>
                      <AccordionContent className="pt-4 pb-2 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <h4 className="font-bold text-slate-700 flex items-center gap-2">
                              <Stethoscope className="w-5 h-5 text-blue-500" />
                              Datos Antropométricos
                            </h4>
                            <div className="text-sm space-y-2 pl-7">
                              {seguimiento.peso ? (
                                <>
                                  <p><strong>Peso:</strong> {seguimiento.peso} kg</p>
                                  <p><strong>Estatura:</strong> {seguimiento.estatura} cm</p>
                                  <p><strong>IMC:</strong> {seguimiento.imc?.toFixed(1) || calculateBMI(seguimiento.peso, seguimiento.estatura || 0)}</p>
                                </>
                              ) : (
                                <p className="text-slate-500">Sin mediciones antropométricas registradas</p>
                              )}
                            </div>
                          </div>
                          <div className="space-y-4">
                            <h4 className="font-bold text-slate-700 flex items-center gap-2">
                              <ClipboardList className="w-5 h-5 text-blue-500" />
                              Observaciones
                            </h4>
                            <p className="text-sm text-slate-600 pl-7">
                              {seguimiento.observacion || "Sin observaciones registradas"}
                            </p>
                          </div>
                        </div>
                        
                        {/* Botón para ver resultados completos */}
                        <div className="flex justify-center pt-4 border-t">
                          <Button
                            onClick={() => {
                              // Guardar el ID del seguimiento para cargar los resultados
                              sessionStorage.setItem('last_seguimiento_id', seguimiento.id_seguimiento.toString())
                              // Crear un objeto Child temporal para pasar a FollowUpResults
                              const tempChild: Child = {
                                id: child.id,
                                name: child.name,
                                age: calculateAge(child.birthDate),
                                gender: child.gender,
                                birthDate: child.birthDate,
                                community: child.community,
                                guardian: child.guardian,
                                phone: child.phone || "N/A",
                                address: child.address || "N/A",
                                status: "normal",
                                lastVisit: seguimiento.fecha,
                                weight: seguimiento.peso || 0,
                                height: seguimiento.estatura || 0,
                                medicalHistory: [],
                                growthHistory: [],
                              }
                              
                              // Crear datos de seguimiento temporales
                              const tempFollowUpData = {
                                childId: child.id,
                                weight: seguimiento.peso?.toString() || "",
                                height: seguimiento.estatura?.toString() || "",
                                armCircumference: "",
                                headCircumference: "",
                                tricepsFold: "",
                                abdominalPerimeter: "",
                                symptoms: [],
                                physicalSigns: [],
                                clinicalObservations: seguimiento.observacion || "",
                                hemoglobin: "",
                                stoolExam: "",
                                urineExam: "",
                                eyePhotos: [],
                                gumPhotos: [],
                                caregiverComments: "",
                              }
                              
                              // Aquí podrías abrir un modal o navegar a los resultados
                              // Por ahora, vamos a usar el componente FollowUpResults
                              setSelectedSeguimiento({
                                child: tempChild,
                                followUpData: tempFollowUpData,
                                seguimientoId: seguimiento.id_seguimiento
                              })
                            }}
                            className={`bg-gradient-to-r ${theme.buttonColor} text-white hover:scale-105 transition-transform`}
                          >
                            <FileText className="w-4 h-4 mr-2" />
                            Ver Evaluación Nutricional Completa
                          </Button>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              ) : (
                <div className="text-center py-10">
                  <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-600">No hay seguimientos registrados para este infante.</p>
                  <p className="text-sm text-slate-500 mt-2">Los seguimientos aparecerán aquí una vez sean registrados.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="crecimiento" className="space-y-6 mt-6">
          {growthHistory.length > 0 ? (
            <GrowthChart 
              childId={child.id} 
              data={growthHistory.map(gh => ({
                date: gh.date,
                weight: gh.weight,
                height: gh.height,
                bmi: gh.bmi,
                age: 0 // TODO: calcular edad en el momento del seguimiento
              }))} 
            />
          ) : (
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
              <CardContent className="py-12 text-center">
                <TrendingUp className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">No hay datos de crecimiento disponibles.</p>
                <p className="text-sm text-slate-500 mt-2">Se necesitan al menos dos seguimientos con mediciones para generar el gráfico.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="reportes" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Generar Reportes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button 
                  variant="outline" 
                  className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
                  disabled
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Reporte Individual PDF
                </Button>
                <Button 
                  variant="outline" 
                  className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
                  disabled
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Gráfico de Crecimiento
                </Button>
                <p className="text-xs text-slate-500 text-center">Funcionalidad en desarrollo</p>
              </CardContent>
            </Card>
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Estadísticas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-600">Total de seguimientos:</span>
                  <span className="font-bold text-slate-800">{seguimientos.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Mediciones registradas:</span>
                  <span className="font-bold text-slate-800">
                    {seguimientos.filter(s => s.peso && s.estatura).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Primer registro:</span>
                  <span className="font-bold text-slate-800">
                    {seguimientos.length > 0 
                      ? new Date(seguimientos.sort((a, b) => 
                          new Date(a.fecha).getTime() - new Date(b.fecha).getTime()
                        )[0].fecha).toLocaleDateString('es-CO')
                      : "N/A"
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Última actualización:</span>
                  <span className="font-bold text-slate-800">
                    {seguimientos.length > 0 
                      ? new Date(seguimientos.sort((a, b) => 
                          new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
                        )[0].fecha).toLocaleDateString('es-CO')
                      : "N/A"
                    }
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}