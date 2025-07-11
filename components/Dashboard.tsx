"use client"

import { Users, Calendar, AlertTriangle, TrendingUp, Activity, UserPlus, Upload, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ThemeColors } from "@/types"
import { mockStats } from "@/data/mockData"

interface DashboardProps {
  theme: ThemeColors
  onNewChild: () => void
  onNavigate: (view: string) => void
}

export function Dashboard({ theme, onNewChild, onNavigate }: DashboardProps) {
  return (
    <div className="space-y-8">
      {/* Título y descripción sin recuadro */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Panel de Control</h1>
        <p className="text-lg text-slate-600">Resumen de actividades y estadísticas del sistema nutricional</p>
      </div>

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card
          className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500 hover:scale-105 cursor-pointer`}
          onClick={() => onNavigate("children")}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total de Niños</CardTitle>
            <Users className={`h-4 w-4 ${theme.accentColor}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-800">{mockStats.totalChildren}</div>
            <p className="text-xs text-slate-500">Registrados en el sistema</p>
          </CardContent>
        </Card>

        <Card
          className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500 hover:scale-105 cursor-pointer`}
          onClick={() => onNavigate("new-followup")}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Seguimientos del Mes</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-800">{mockStats.monthlyFollowUps}</div>
            <p className="text-xs text-slate-500">Enero 2024</p>
          </CardContent>
        </Card>

        <Card
          className={`${theme.cardBorder} bg-gradient-to-br from-white to-orange-50 transition-all duration-500 hover:scale-105 cursor-pointer`}
          onClick={() => onNavigate("children")}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Alertas Activas</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-800">{mockStats.activeAlerts}</div>
            <p className="text-xs text-slate-500">Requieren atención</p>
          </CardContent>
        </Card>

        <Card
          className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500 hover:scale-105 cursor-pointer`}
          onClick={() => onNavigate("reports")}
        >
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Evaluaciones Completadas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-800">{mockStats.completedAssessments}</div>
            <p className="text-xs text-slate-500">Este mes</p>
          </CardContent>
        </Card>
      </div>

      {/* Acciones rápidas sin recuadro */}
      <div className="text-center space-y-6">
        <div className="flex items-center justify-center gap-2 mb-6">
          <Activity className={`w-6 h-6 ${theme.accentColor}`} />
          <h2 className="text-2xl font-bold text-slate-800">Acciones Rápidas</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <Button
            onClick={onNewChild}
            className={`h-16 bg-gradient-to-r ${theme.buttonColor} text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105 shadow-lg`}
          >
            <UserPlus className="w-5 h-5 mr-3" />
            Nuevo Niño
          </Button>
          <Button
            onClick={() => onNavigate("import-data")}
            variant="outline"
            className={`h-16 ${theme.cardBorder} hover:bg-opacity-50 bg-white/50 backdrop-blur-sm transition-all duration-300 hover:scale-105 shadow-lg rounded-xl`}
          >
            <Upload className="w-5 h-5 mr-3" />
            Importar Datos
          </Button>
          <Button
            onClick={() => onNavigate("generate-reports")}
            variant="outline"
            className={`h-16 ${theme.cardBorder} hover:bg-opacity-50 bg-white/50 backdrop-blur-sm transition-all duration-300 hover:scale-105 shadow-lg rounded-xl`}
          >
            <BarChart3 className="w-5 h-5 mr-3" />
            Generar Reportes
          </Button>
        </div>
      </div>
    </div>
  )
}
