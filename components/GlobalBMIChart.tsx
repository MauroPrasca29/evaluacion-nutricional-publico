"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState } from "react"
import type { GlobalBMIStats, ThemeColors } from "@/types"

const globalBMIData = [
  { ageGroup: "0-2 años", normal: 45, riesgo: 8, moderado: 3, severo: 1 },
  { ageGroup: "3-5 años", normal: 52, riesgo: 7, moderado: 4, severo: 2 },
  { ageGroup: "6-8 años", normal: 38, riesgo: 5, moderado: 2, severo: 1 },
  { ageGroup: "9-11 años", normal: 21, riesgo: 3, moderado: 1, severo: 1 },
]

const sedeData = [
  { sede: "Centro", total: 85, normal: 62, alertas: 23 },
  { sede: "Norte", total: 67, normal: 48, alertas: 19 },
  { sede: "Sur", total: 58, normal: 46, alertas: 12 },
]

const COLORS = ["#10b981", "#f59e0b", "#ef4444", "#7c2d12"]

interface GlobalBMIChartProps {
  data?: GlobalBMIStats
  theme?: ThemeColors
}

export function GlobalBMIChart({ data, theme }: GlobalBMIChartProps) {
  const [selectedSede, setSelectedSede] = useState("todas")

  const pieData = [
    { name: "Normal", value: 156, color: "#10b981" },
    { name: "Riesgo", value: 23, color: "#f59e0b" },
    { name: "Moderado", value: 10, color: "#ef4444" },
    { name: "Severo", value: 5, color: "#7c2d12" },
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
            <Select value={selectedSede} onValueChange={setSelectedSede}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrar por sede" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas las sedes</SelectItem>
                <SelectItem value="centro">Centro</SelectItem>
                <SelectItem value="norte">Norte</SelectItem>
                <SelectItem value="sur">Sur</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={globalBMIData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ageGroup" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="normal" stackId="a" fill="#10b981" name="Normal" />
                <Bar dataKey="riesgo" stackId="a" fill="#f59e0b" name="Riesgo" />
                <Bar dataKey="moderado" stackId="a" fill="#ef4444" name="Moderado" />
                <Bar dataKey="severo" stackId="a" fill="#7c2d12" name="Severo" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

        <Card>
          <CardHeader>
            <CardTitle>Estadísticas por Sede</CardTitle>
            <CardDescription>Distribución de niños por ubicación</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {sedeData.map((sede, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{sede.sede}</span>
                    <span className="text-sm text-gray-600">{sede.total} niños</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(sede.normal / sede.total) * 100}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Normal: {sede.normal}</span>
                    <span>Alertas: {sede.alertas}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
