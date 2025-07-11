"use client"

import { useState } from "react"
import { PieChart, TrendingUp, Users, Filter } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { ThemeColors } from "@/types"

interface AdvancedStatisticsProps {
  theme: ThemeColors
}

export function AdvancedStatistics({ theme }: AdvancedStatisticsProps) {
  const [selectedPeriod, setSelectedPeriod] = useState("month")
  const [selectedCommunity, setSelectedCommunity] = useState("all")
  const [selectedMetric, setSelectedMetric] = useState("nutritional-status")

  // Datos simulados para gráficos
  const nutritionalStatusData = [
    { status: "Normal", count: 118, percentage: 75.6, color: "bg-green-500" },
    { status: "Alerta", count: 28, percentage: 17.9, color: "bg-orange-500" },
    { status: "Seguimiento", count: 10, percentage: 6.4, color: "bg-blue-500" },
  ]

  const ageGroupData = [
    { group: "0-2 años", count: 45, percentage: 28.8 },
    { group: "3-5 años", count: 62, percentage: 39.7 },
    { group: "6-12 años", count: 49, percentage: 31.4 },
  ]

  const genderData = [
    { gender: "Femenino", count: 82, percentage: 52.6 },
    { gender: "Masculino", count: 74, percentage: 47.4 },
  ]

  const communityData = [
    { community: "Villa Esperanza", count: 68, alerts: 12 },
    { community: "San José", count: 45, alerts: 8 },
    { community: "El Progreso", count: 43, alerts: 6 },
  ]

  const monthlyTrends = [
    { month: "Ene", evaluations: 42, alerts: 8 },
    { month: "Feb", evaluations: 38, alerts: 6 },
    { month: "Mar", evaluations: 45, alerts: 9 },
    { month: "Abr", evaluations: 52, alerts: 11 },
    { month: "May", evaluations: 48, alerts: 7 },
    { month: "Jun", evaluations: 55, alerts: 12 },
  ]

  const bmiDistribution = [
    { range: "Bajo peso", count: 15, percentage: 9.6 },
    { range: "Normal", count: 118, percentage: 75.6 },
    { range: "Sobrepeso", count: 18, percentage: 11.5 },
    { range: "Obesidad", count: 5, percentage: 3.2 },
  ]

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Estadísticas Avanzadas</h1>
        <p className="text-lg text-slate-600">Análisis detallado y visualización de datos nutricionales</p>
      </div>

      {/* Filtros */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
        <CardHeader>
          <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filtros de Análisis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Período</label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Última semana</SelectItem>
                  <SelectItem value="month">Último mes</SelectItem>
                  <SelectItem value="quarter">Último trimestre</SelectItem>
                  <SelectItem value="year">Último año</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Comunidad</label>
              <Select value={selectedCommunity} onValueChange={setSelectedCommunity}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="villa-esperanza">Villa Esperanza</SelectItem>
                  <SelectItem value="san-jose">San José</SelectItem>
                  <SelectItem value="el-progreso">El Progreso</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Métrica</label>
              <Select value={selectedMetric} onValueChange={setSelectedMetric}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="nutritional-status">Estado Nutricional</SelectItem>
                  <SelectItem value="age-groups">Grupos de Edad</SelectItem>
                  <SelectItem value="bmi-distribution">Distribución IMC</SelectItem>
                  <SelectItem value="growth-trends">Tendencias de Crecimiento</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button className={`bg-gradient-to-r ${theme.buttonColor} text-white`}>Actualizar</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Estado Nutricional */}
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Estado Nutricional
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Gráfico circular simulado */}
              <div className="relative w-48 h-48 mx-auto">
                <div className="absolute inset-0 rounded-full bg-gradient-to-r from-green-400 via-orange-400 to-blue-400"></div>
                <div className="absolute inset-4 rounded-full bg-white flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-800">156</div>
                    <div className="text-sm text-slate-600">Total</div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {nutritionalStatusData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-4 h-4 rounded ${item.color}`}></div>
                      <span className="text-sm font-medium text-slate-700">{item.status}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-slate-800">{item.count}</div>
                      <div className="text-xs text-slate-500">{item.percentage}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Distribución por Edad */}
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Distribución por Edad
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {ageGroupData.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-700">{item.group}</span>
                    <span className="text-sm font-bold text-slate-800">
                      {item.count} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-400 to-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${item.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Estadísticas por comunidad */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50 transition-all duration-500`}>
        <CardHeader>
          <CardTitle className="text-xl font-bold text-slate-800">Estadísticas por Comunidad</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {communityData.map((community, index) => (
              <div key={index} className="bg-white p-4 rounded-lg border border-slate-200">
                <h4 className="font-semibold text-slate-800 mb-3">{community.community}</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Total niños:</span>
                    <span className="font-bold text-slate-800">{community.count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">Alertas:</span>
                    <Badge variant={community.alerts > 10 ? "destructive" : "secondary"}>{community.alerts}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">% del total:</span>
                    <span className="font-bold text-slate-800">{((community.count / 156) * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tendencias mensuales */}
      <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-orange-50 transition-all duration-500`}>
        <CardHeader>
          <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Tendencias Mensuales
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-6 gap-4">
              {monthlyTrends.map((month, index) => (
                <div key={index} className="text-center">
                  <div className="bg-white p-3 rounded-lg border border-slate-200 mb-2">
                    <div className="text-lg font-bold text-slate-800">{month.evaluations}</div>
                    <div className="text-xs text-slate-600">Evaluaciones</div>
                    <div className="text-sm font-semibold text-orange-600 mt-1">{month.alerts}</div>
                    <div className="text-xs text-slate-600">Alertas</div>
                  </div>
                  <div className="text-sm font-medium text-slate-700">{month.month}</div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Distribución IMC */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-yellow-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Distribución IMC</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bmiDistribution.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-700">{item.range}</span>
                    <span className="text-sm font-bold text-slate-800">
                      {item.count} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        item.range === "Normal"
                          ? "bg-green-500"
                          : item.range === "Bajo peso"
                            ? "bg-blue-500"
                            : item.range === "Sobrepeso"
                              ? "bg-orange-500"
                              : "bg-red-500"
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-pink-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Distribución por Género</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {genderData.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-slate-700">{item.gender}</span>
                    <span className="text-sm font-bold text-slate-800">
                      {item.count} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${
                        item.gender === "Femenino" ? "bg-pink-500" : "bg-blue-500"
                      }`}
                      style={{ width: `${item.percentage}%` }}
                    ></div>
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
