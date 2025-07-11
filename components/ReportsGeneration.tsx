"use client"

import { useState } from "react"
import { FileText, Download, Filter, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import type { ThemeColors } from "@/types"

interface ReportsGenerationProps {
  theme: ThemeColors
}

export function ReportsGeneration({ theme }: ReportsGenerationProps) {
  const [reportType, setReportType] = useState("")
  const [dateRange, setDateRange] = useState({ start: "", end: "" })
  const [filters, setFilters] = useState({
    community: "",
    ageRange: "",
    gender: "",
    nutritionalStatus: "",
  })
  const [selectedFields, setSelectedFields] = useState<string[]>([])
  const [generating, setGenerating] = useState(false)

  const reportTypes = [
    { value: "individual", label: "Reporte Individual", description: "Reporte detallado de un niño específico" },
    { value: "community", label: "Reporte por Comunidad", description: "Estadísticas agrupadas por comunidad" },
    { value: "nutritional", label: "Estado Nutricional", description: "Análisis del estado nutricional general" },
    { value: "growth", label: "Crecimiento", description: "Seguimiento de crecimiento y desarrollo" },
    { value: "alerts", label: "Alertas y Seguimientos", description: "Casos que requieren atención especial" },
    { value: "comprehensive", label: "Reporte Integral", description: "Reporte completo con todas las métricas" },
  ]

  const availableFields = [
    "Información personal",
    "Datos antropométricos",
    "Historial médico",
    "Gráficos de crecimiento",
    "Observaciones clínicas",
    "Exámenes complementarios",
    "Fotografías clínicas",
    "Recomendaciones",
    "Estadísticas comparativas",
  ]

  const handleFieldToggle = (field: string) => {
    setSelectedFields((prev) => (prev.includes(field) ? prev.filter((f) => f !== field) : [...prev, field]))
  }

  const generateReport = async () => {
    if (!reportType) {
      alert("Por favor selecciona un tipo de reporte")
      return
    }

    setGenerating(true)

    // Simular generación de reporte
    await new Promise((resolve) => setTimeout(resolve, 3000))

    alert("Reporte generado exitosamente")
    setGenerating(false)
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Generar Reportes</h1>
        <p className="text-lg text-slate-600">Crea reportes personalizados y análisis detallados</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Configuración del reporte */}
        <div className="lg:col-span-2 space-y-6">
          {/* Tipo de reporte */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Tipo de Reporte
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportTypes.map((type) => (
                  <div
                    key={type.value}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      reportType === type.value
                        ? `border-amber-400 bg-amber-50 shadow-md`
                        : `border-slate-200 hover:border-amber-300 hover:bg-amber-50/50`
                    }`}
                    onClick={() => setReportType(type.value)}
                  >
                    <h4 className="font-semibold text-slate-800">{type.label}</h4>
                    <p className="text-sm text-slate-600 mt-1">{type.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Filtros */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filtros y Criterios
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Rango de fechas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startDate">Fecha de inicio</Label>
                  <Input
                    id="startDate"
                    type="date"
                    value={dateRange.start}
                    onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                    className="border-amber-200 focus:border-amber-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endDate">Fecha de fin</Label>
                  <Input
                    id="endDate"
                    type="date"
                    value={dateRange.end}
                    onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                    className="border-amber-200 focus:border-amber-400"
                  />
                </div>
              </div>

              {/* Otros filtros */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Comunidad</Label>
                  <Select
                    value={filters.community}
                    onValueChange={(value) => setFilters({ ...filters, community: value })}
                  >
                    <SelectTrigger className="border-amber-200 focus:border-amber-400">
                      <SelectValue placeholder="Todas las comunidades" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas las comunidades</SelectItem>
                      <SelectItem value="villa-esperanza">Villa Esperanza</SelectItem>
                      <SelectItem value="san-jose">San José</SelectItem>
                      <SelectItem value="el-progreso">El Progreso</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Rango de edad</Label>
                  <Select
                    value={filters.ageRange}
                    onValueChange={(value) => setFilters({ ...filters, ageRange: value })}
                  >
                    <SelectTrigger className="border-amber-200 focus:border-amber-400">
                      <SelectValue placeholder="Todas las edades" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas las edades</SelectItem>
                      <SelectItem value="0-2">0-2 años</SelectItem>
                      <SelectItem value="3-5">3-5 años</SelectItem>
                      <SelectItem value="6-12">6-12 años</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Género</Label>
                  <Select value={filters.gender} onValueChange={(value) => setFilters({ ...filters, gender: value })}>
                    <SelectTrigger className="border-amber-200 focus:border-amber-400">
                      <SelectValue placeholder="Todos los géneros" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los géneros</SelectItem>
                      <SelectItem value="masculino">Masculino</SelectItem>
                      <SelectItem value="femenino">Femenino</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Estado nutricional</Label>
                  <Select
                    value={filters.nutritionalStatus}
                    onValueChange={(value) => setFilters({ ...filters, nutritionalStatus: value })}
                  >
                    <SelectTrigger className="border-amber-200 focus:border-amber-400">
                      <SelectValue placeholder="Todos los estados" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los estados</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="alerta">Alerta</SelectItem>
                      <SelectItem value="seguimiento">Seguimiento</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Campos a incluir */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800">Campos a Incluir</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {availableFields.map((field) => (
                  <div key={field} className="flex items-center space-x-2">
                    <Checkbox
                      id={`field-${field}`}
                      checked={selectedFields.includes(field)}
                      onCheckedChange={() => handleFieldToggle(field)}
                    />
                    <Label htmlFor={`field-${field}`} className="text-sm">
                      {field}
                    </Label>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Panel de acciones */}
        <div className="space-y-6">
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50 transition-all duration-500`}>
            <CardHeader>
              <CardTitle className="text-xl font-bold text-slate-800">Generar Reporte</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    Tipo: {reportTypes.find((t) => t.value === reportType)?.label || "No seleccionado"}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    Campos: {selectedFields.length} seleccionados
                  </Badge>
                </div>
              </div>

              <Button
                onClick={generateReport}
                disabled={!reportType || generating}
                className={`w-full bg-gradient-to-r ${theme.buttonColor} text-white transition-all duration-300 hover:scale-105`}
              >
                {generating ? (
                  <>
                    <BarChart3 className="w-4 h-4 mr-2 animate-spin" />
                    Generando...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Generar PDF
                  </>
                )}
              </Button>

              <Button
                variant="outline"
                disabled={!reportType || generating}
                className={`w-full ${theme.cardBorder} hover:bg-opacity-50 bg-transparent`}
              >
                <Download className="w-4 h-4 mr-2" />
                Generar Excel
              </Button>
            </CardContent>
          </Card>

          {/* Reportes recientes */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-orange-50 transition-all duration-500`}>
            <CardHeader>
              <CardTitle className="text-lg font-bold text-slate-800">Reportes Recientes</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { name: "Reporte Nutricional Enero", date: "2024-01-15", type: "PDF" },
                { name: "Estado por Comunidades", date: "2024-01-10", type: "Excel" },
                { name: "Seguimientos Pendientes", date: "2024-01-08", type: "PDF" },
              ].map((report, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{report.name}</p>
                    <p className="text-xs text-slate-500">{report.date}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {report.type}
                    </Badge>
                    <Button size="sm" variant="ghost">
                      <Download className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
