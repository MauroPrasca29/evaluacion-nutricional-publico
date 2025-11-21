"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState, useEffect } from "react"
import type { ThemeColors } from "@/types"

const COLORS = ["#10b981", "#f59e0b", "#ef4444", "#7c2d12"]

interface GlobalBMIChartProps {
  theme?: ThemeColors
}

interface NutritionalStats {
  por_edad: Array<{
    ageGroup: string
    normal: number
    bajo: number
    medio: number
    alto: number
  }>
  general: {
    normal: number
    bajo: number
    medio: number
    alto: number
  }
  por_genero: Array<{
    genero: string
    normal: number
    bajo: number
    medio: number
    alto: number
  }>
  por_sede: Array<{
    sede: string
    total: number
    normal: number
    alertas: number
  }>
}

export function GlobalBMIChart({ theme }: GlobalBMIChartProps) {
  const [selectedSede, setSelectedSede] = useState("todas")
  const [stats, setStats] = useState<NutritionalStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/children/nutritional-stats')
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        }
      } catch (error) {
        console.error('Error cargando estadísticas nutricionales:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading || !stats) {
    return <div className="text-center py-8">Cargando estadísticas...</div>
  }

  const pieData = [
    { name: "Normal", value: stats.general.normal, color: "#10b981" },
    { name: "Riesgo", value: stats.general.bajo, color: "#f59e0b" },
    { name: "Moderado", value: stats.general.medio, color: "#ef4444" },
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Estado Nutricional Global por Edad</CardTitle>
              <CardDescription>Distribución del IMC por grupos de edad</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.por_edad} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ageGroup" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="normal" stackId="a" fill="#10b981" name="Normal" />
                <Bar dataKey="bajo" stackId="a" fill="#f59e0b" name="Riesgo" />
                <Bar dataKey="medio" stackId="a" fill="#ef4444" name="Moderado" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribución General */}
        <Card>
          <CardHeader>
            <CardTitle>Distribución General</CardTitle>
            <CardDescription>Estado nutricional de todos los niños</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {pieData.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm">
                    {item.name}: {item.value}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Distribución por Género */}
        <Card>
          <CardHeader>
            <CardTitle>Distribución por Género</CardTitle>
            <CardDescription>Estado nutricional por sexo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.por_genero} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="genero" type="category" />
                  <Tooltip />
                  <Bar dataKey="normal" stackId="a" fill="#10b981" name="Normal" />
                  <Bar dataKey="bajo" stackId="a" fill="#f59e0b" name="Riesgo" />
                  <Bar dataKey="medio" stackId="a" fill="#ef4444" name="Moderado" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}