"use client"

import { Users, AlertTriangle, ClipboardList, Calendar, UserPlus, FileText, Upload } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { GlobalBMIChart } from "@/components/GlobalBMIChart"
import { mockStats, mockGlobalBMIStats, mockAppointments, mockRecentActivity } from "@/data/mockData"
import type { ThemeColors } from "@/types"

interface DashboardProps {
  theme: ThemeColors
  onNewChild?: () => void
  onNavigate?: (view: string) => void
}

export function Dashboard({ theme }: DashboardProps) {

  const iconMap = {
    "user-plus": <UserPlus className="w-5 h-5 text-blue-500" />,
    "file-text": <FileText className="w-5 h-5 text-green-500" />,
    "alert-triangle": <AlertTriangle className="w-5 h-5 text-orange-500" />,
    upload: <Upload className="w-5 h-5 text-purple-500" />,
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800">Panel de Control General</h1>
        <p className="text-slate-600">Resumen del estado nutricional y actividades de la institución.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total de Niños</CardTitle>
            <Users className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">{mockStats.totalChildren}</div>
            <p className="text-xs text-slate-500">+2% que el mes pasado</p>
          </CardContent>
        </Card>
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Alertas Activas</CardTitle>
            <AlertTriangle className="h-5 w-5 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">{mockStats.activeAlerts}</div>
            <p className="text-xs text-slate-500">3 nuevas esta semana</p>
          </CardContent>
        </Card>
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Evaluaciones Pendientes</CardTitle>
            <ClipboardList className="h-5 w-5 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">{mockStats.pendingAssessments}</div>
            <p className="text-xs text-slate-500">5 vencen esta semana</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Global BMI Chart */}
        <div className="lg:col-span-2">
          <GlobalBMIChart data={mockGlobalBMIStats} theme={theme} />
        </div>

        {/* Side Column */}
        <div className="space-y-8">
          {/* Próximos Seguimientos */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Calendar className="w-5 h-5 text-indigo-500" />
                Próximos Seguimientos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockAppointments.slice(0, 4).map((item) => (
                <div key={item.id} className="flex items-center gap-4">
                  <div className="flex-shrink-0 bg-indigo-100 rounded-lg p-2">
                    <Calendar className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-800">{item.child}</p>
                    <p className="text-sm text-slate-500">
                      {item.time} - {item.type}
                    </p>
                  </div>
                  <Badge variant="outline" className="ml-auto">
                    {new Date(item.date).toLocaleDateString("es-ES", { day: "2-digit", month: "short" })}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Actividad Reciente */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="w-5 h-5 text-green-500" />
                Actividad Reciente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockRecentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-4">
                  <div className="flex-shrink-0 bg-slate-100 rounded-full p-2 mt-1">
                    {iconMap[activity.icon as keyof typeof iconMap]}
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">
                      {activity.text} <span className="font-semibold text-slate-800">{activity.subject}</span>
                    </p>
                    <p className="text-xs text-slate-400">{activity.time}</p>
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
