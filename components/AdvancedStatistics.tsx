"use client"

import { useState } from "react"
import { BarChart3, PieChart, Users, Filter, Download, TrendingUp, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import type { ThemeColors } from "@/types"

interface AdvancedStatisticsProps {
  theme: ThemeColors
}

export function AdvancedStatistics({ theme }: AdvancedStatisticsProps) {
  const [selectedSede, setSelectedSede] = useState("todas")
  const [selectedAge, setSelectedAge] = useState("todos")

  // Datos simulados para las estadísticas
  const nutritionalStats = {
    normal: 156,
    underweight: 23,
    overweight: 18,
    obesity: 8,
    severe: 5
  }

  const monthlyTrends = [
    { month: "Enero", evaluations: 45, alerts: 8 },
    { month: "Febrero", evaluations: 52, alerts: 6 },
    { month: "Marzo", evaluations: 48, alerts: 9 },
    { month: "Abril", evaluations: 55, alerts: 7 },
    { month: "Mayo", evaluations: 61, alerts: 5 },
    { month: "Junio", evaluations: 58, alerts: 8 }
  ]

  const sedeStats = [
    { name: "Sede Norte", children: 89, alerts: 12 },
    { name: "Sede Sur", children: 76, alerts: 8 },
    { name: "Sede Centro", children: 73, alerts: 9 }
  ]

  const total = nutritionalStats.normal + nutritionalStats.underweight + nutritionalStats.overweight + nutritionalStats.obesity + nutritionalStats.severe

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Estadísticas Avanzadas</h1>
        <p className="text-slate-600">Análisis detallado del estado nutricional de la población infantil.</p>
      </div>

      {/* Filtros */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-blue-600" />
            <CardTitle>Filtros de Análisis</CardTitle>
          </div>
          <Button variant="outline" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Exportar Reporte
          </Button>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Sede</label>
            <Select value={selectedSede} onValueChange={setSelectedSede}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar sede" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas las sedes</SelectItem>
                <SelectItem value="norte">Sede Norte</SelectItem>
                <SelectItem value="sur">Sede Sur</SelectItem>
                <SelectItem value="centro">Sede Centro</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Rango de Edad</label>
            <Select value={selectedAge} onValueChange={setSelectedAge}>
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar rango" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos los rangos</SelectItem>
                <SelectItem value="0-2">0-2 años</SelectItem>
                <SelectItem value="3-5">3-5 años</SelectItem>
                <SelectItem value="6-11">6-11 años</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">Período</label>
            <Select defaultValue="6meses">
              <SelectTrigger>
                <SelectValue placeholder="Seleccionar período" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1mes">Último mes</SelectItem>
                <SelectItem value="3meses">Últimos 3 meses</SelectItem>
                <SelectItem value="6meses">Últimos 6 meses</SelectItem>
                <SelectItem value="1ano">Último año</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Estadísticas Principales */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-green-50 to-green-100`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700">Estado Normal</CardTitle>
            <Users className="h-5 w-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-800">{nutritionalStats.normal}</div>
            <p className="text-xs text-green-600">
              {((nutritionalStats.normal / total) * 100).toFixed(1)}% del total
            </p>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br from-orange-50 to-orange-100`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700">Bajo Peso</CardTitle>
            <TrendingUp className="h-5 w-5 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-800">{nutritionalStats.underweight}</div>
            <p className="text-xs text-orange-600">
              {((nutritionalStats.underweight / total) * 100).toFixed(1)}% del total
            </p>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br from-yellow-50 to-yellow-100`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-yellow-700">Sobrepeso</CardTitle>
            <BarChart3 className="h-5 w-5 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-800">{nutritionalStats.overweight}</div>
            <p className="text-xs text-yellow-600">
              {((nutritionalStats.overweight / total) * 100).toFixed(1)}% del total
            </p>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br from-red-50 to-red-100`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-red-700">Casos Severos</CardTitle>
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-800">{nutritionalStats.severe}</div>
            <p className="text-xs text-red-600">
              {((nutritionalStats.severe / total) * 100).toFixed(1)}% del total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Análisis por Sede */}
      <div className="grid gap-8 lg:grid-cols-2">
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-blue-600" />
              Distribución por Sede
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {sedeStats.map((sede, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <h3 className="font-semibold text-slate-800">{sede.name}</h3>
                  <p className="text-sm text-slate-600">{sede.children} niños registrados</p>
                </div>
                <div className="text-right">
                  <Badge variant={sede.alerts > 10 ? "destructive" : sede.alerts > 5 ? "default" : "secondary"}>
                    {sede.alerts} alertas
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-green-600" />
              Tendencia Mensual
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {monthlyTrends.map((month, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                <div>
                  <h3 className="font-semibold text-slate-800">{month.month}</h3>
                  <p className="text-sm text-slate-600">{month.evaluations} evaluaciones</p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-slate-800">{month.alerts}</div>
                  <p className="text-xs text-slate-500">alertas</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Resumen de Acciones Recomendadas */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br from-blue-50 to-indigo-100`}>
        <CardHeader>
          <CardTitle className="text-blue-800">Acciones Recomendadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-semibold text-blue-700">Prioridad Alta</h4>
              <ul className="space-y-1 text-sm text-blue-600">
                <li>• Seguimiento inmediato de 5 casos severos</li>
                <li>• Revisión de protocolos en Sede Norte</li>
                <li>• Capacitación en detección temprana</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-blue-700">Prioridad Media</h4>
              <ul className="space-y-1 text-sm text-blue-600">
                <li>• Programa preventivo para sobrepeso</li>
                <li>• Mejora en registro de datos</li>
                <li>• Coordinación entre sedes</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
