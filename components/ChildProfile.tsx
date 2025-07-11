"use client"
import { ArrowLeft, User, FileText, TrendingUp, Calendar, Phone, Weight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { Child, ThemeColors } from "@/types"

interface ChildProfileProps {
  child: Child
  theme: ThemeColors
  onBack: () => void
}

export function ChildProfile({ child, theme, onBack }: ChildProfileProps) {
  const calculateAge = (birthDate: string) => {
    const today = new Date()
    const birth = new Date(birthDate)
    const age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      return age - 1
    }
    return age
  }

  const calculateBMI = (weight: number, height: number) => {
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
              Estado: {child.status}
            </Badge>
          </div>
        </div>
      </div>

      {/* Tabs del perfil */}
      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="historial" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Historial Médico
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
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-800">Historial Médico</h3>
            {child.medicalHistory.length > 0 ? (
              child.medicalHistory.map((record) => (
                <Card key={record.id} className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-bold text-slate-800">Consulta del {record.date}</h4>
                        <Badge
                          className={`mt-1 ${
                            record.nutritionalStatus === "normal"
                              ? "bg-green-100 text-green-800"
                              : record.nutritionalStatus === "alerta"
                                ? "bg-orange-100 text-orange-800"
                                : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {record.nutritionalStatus}
                        </Badge>
                      </div>
                      <div className="text-right text-sm text-slate-600">
                        <p>Peso: {record.weight} kg</p>
                        <p>Talla: {record.height} cm</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p>
                        <strong>Observaciones:</strong> {record.observations}
                      </p>
                      <p>
                        <strong>Recomendaciones:</strong> {record.recommendations}
                      </p>
                      {record.vaccinations.length > 0 && (
                        <p>
                          <strong>Vacunas:</strong> {record.vaccinations.join(", ")}
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
                <CardContent className="p-6 text-center">
                  <p className="text-slate-600">No hay registros médicos disponibles</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="crecimiento" className="space-y-6 mt-6">
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-800">Historial de Crecimiento</h3>
            {child.growthHistory.length > 0 ? (
              <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
                <CardContent className="p-6">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Fecha</th>
                          <th className="text-left py-2">Peso (kg)</th>
                          <th className="text-left py-2">Talla (cm)</th>
                          <th className="text-left py-2">IMC</th>
                        </tr>
                      </thead>
                      <tbody>
                        {child.growthHistory.map((record, index) => (
                          <tr key={index} className="border-b">
                            <td className="py-2">{record.date}</td>
                            <td className="py-2">{record.weight}</td>
                            <td className="py-2">{record.height}</td>
                            <td className="py-2">{record.bmi}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
                <CardContent className="p-6 text-center">
                  <p className="text-slate-600">No hay datos de crecimiento disponibles</p>
                </CardContent>
              </Card>
            )}
          </div>
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
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Reporte Individual PDF
                </Button>
                <Button
                  variant="outline"
                  className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Gráfico de Crecimiento
                </Button>
              </CardContent>
            </Card>

            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
              <CardHeader>
                <CardTitle className="text-lg font-bold text-slate-800">Estadísticas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-600">Total de consultas:</span>
                  <span className="font-bold text-slate-800">{child.medicalHistory.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Registros de crecimiento:</span>
                  <span className="font-bold text-slate-800">{child.growthHistory.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Estado actual:</span>
                  <Badge
                    className={`${
                      child.status === "normal" ? "bg-green-100 text-green-800" : "bg-orange-100 text-orange-800"
                    }`}
                  >
                    {child.status}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
