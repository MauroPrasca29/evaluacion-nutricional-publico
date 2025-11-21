"use client"

import { Users, AlertTriangle, UserPlus, FileText, Upload } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { GlobalBMIChart } from "@/components/GlobalBMIChart"
import { mockGlobalBMIStats, mockRecentActivity } from "@/data/mockData"
import type { ThemeColors } from "@/types"

interface DashboardProps {
  theme: ThemeColors
  onNewChild?: () => void
  onNavigate?: (view: string) => void
}

interface DashboardStats {
  total_children: number
  active_alerts: number
}

export function Dashboard({ theme }: DashboardProps) {
  const [stats, setStats] = useState<DashboardStats>({
    total_children: 0,
    active_alerts: 0
  })
  const [loading, setLoading] = useState(true)
  const [recentActivity, setRecentActivity] = useState<any[]>([])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [statsRes, activityRes] = await Promise.all([
          fetch('/api/children/stats'),
          fetch('/api/children/recent-activity')
        ])
        
        if (statsRes.ok) {
          const data = await statsRes.json()
          setStats(data)
        }
        
        if (activityRes.ok) {
          const data = await activityRes.json()
          setRecentActivity(data)
        }
      } catch (error) {
        console.error('Error cargando datos:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

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

      {/* Stats Cards - Solo Total de Niños y Alertas Activas */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Total de Niños</CardTitle>
            <Users className="h-5 w-5 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {loading ? '...' : stats.total_children}
            </div>
            <p className="text-xs text-slate-500">Registrados en el sistema</p>
          </CardContent>
        </Card>
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">Alertas Activas</CardTitle>
            <AlertTriangle className="h-5 w-5 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-800">
              {loading ? '...' : stats.active_alerts}
            </div>
            <p className="text-xs text-slate-500">Niños con riesgo alto</p>
          </CardContent>
        </Card>
      </div>

      {/* Global BMI Chart - Ahora ocupa todo el ancho */}
      <div>
        <GlobalBMIChart theme={theme} />
      </div>

      {/* Actividad Reciente - Ahora como sección completa */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="w-5 h-5 text-green-500" />
            Actividad Reciente
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-start gap-4">
              <div className="flex-shrink-0 bg-slate-100 rounded-full p-2 mt-1">
                {iconMap[activity.icon as keyof typeof iconMap]}
              </div>
              <div className="flex-1">
                <p className="text-sm text-slate-600">
                  {activity.text} <span className="font-semibold text-slate-800">{activity.subject}</span>
                </p>
                <p className="text-xs text-slate-400">
                  {activity.usuario && <span className="font-medium">{activity.usuario}</span>}
                  {activity.usuario && ' • '}
                  {activity.time}
                </p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}