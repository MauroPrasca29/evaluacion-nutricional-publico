"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { BarChart3, Filter } from "lucide-react"
import type { GlobalBMIStats, ThemeColors } from "@/types"

interface GlobalBMIChartProps {
  data: GlobalBMIStats
  theme: ThemeColors
}

export function GlobalBMIChart({ data, theme }: GlobalBMIChartProps) {
  const [selectedAgeGroup, setSelectedAgeGroup] = useState<"0-5" | "6-11">("0-5")
  const [selectedSede, setSelectedSede] = useState("todas")

  const currentData = data[selectedAgeGroup]
  const total =
    currentData.severeUnderweight +
    currentData.underweight +
    currentData.normal +
    currentData.overweight +
    currentData.obesity

  const categories = [
    {
      name: "Desnutrición Severa",
      value: currentData.severeUnderweight,
      color: "bg-red-500",
      bgColor: "bg-red-50",
      textColor: "text-red-800",
    },
    {
      name: "Bajo Peso",
      value: currentData.underweight,
      color: "bg-orange-500",
      bgColor: "bg-orange-50",
      textColor: "text-orange-800",
    },
    {
      name: "Normal",
      value: currentData.normal,
      color: "bg-green-500",
      bgColor: "bg-green-50",
      textColor: "text-green-800",
    },
    {
      name: "Sobrepeso",
      value: currentData.overweight,
      color: "bg-yellow-500",
      bgColor: "bg-yellow-50",
      textColor: "text-yellow-800",
    },
    {
      name: "Obesidad",
      value: currentData.obesity,
      color: "bg-red-600",
      bgColor: "bg-red-50",
      textColor: "text-red-900",
    },
  ]

  return (
    <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Estadísticas Globales de IMC
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-500" />
          </div>
        </CardTitle>
        <div className="flex gap-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Grupo de Edad</label>
            <Select value={selectedAgeGroup} onValueChange={(value: "0-5" | "6-11") => setSelectedAgeGroup(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0-5">0-5 años</SelectItem>
                <SelectItem value="6-11">6-11 años</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1 block">Sede</label>
            <Select value={selectedSede} onValueChange={setSelectedSede}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas</SelectItem>
                <SelectItem value="norte">Sede Norte</SelectItem>
                <SelectItem value="sur">Sede Sur</SelectItem>
                <SelectItem value="centro">Sede Centro</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Gráfico de barras visual */}
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-800">
            Distribución por Estado Nutricional ({selectedAgeGroup} años)
          </h3>
          {categories.map((category) => {
            const percentage = total > 0 ? (category.value / total) * 100 : 0
            return (
              <div key={category.name} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-700">{category.name}</span>
                  <Badge className={`${category.bgColor} ${category.textColor}`}>
                    {category.value} ({percentage.toFixed(1)}%)
                  </Badge>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-3">
                  <div
                    className={`${category.color} h-3 rounded-full transition-all duration-500 ease-out`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Resumen estadístico */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-800">{total}</div>
            <div className="text-sm text-slate-600">Total de niños</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {total > 0 ? ((currentData.normal / total) * 100).toFixed(1) : 0}%
            </div>
            <div className="text-sm text-slate-600">Estado normal</div>
          </div>
        </div>

        {/* Indicadores de alerta */}
        {(currentData.severeUnderweight > 0 || currentData.obesity > 5) && (
          <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r-lg">
            <div className="flex items-center">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-orange-800">Atención Requerida</h3>
                <div className="mt-2 text-sm text-orange-700">
                  {currentData.severeUnderweight > 0 && (
                    <p>
                      • {currentData.severeUnderweight} casos de desnutrición severa requieren intervención inmediata
                    </p>
                  )}
                  {currentData.obesity > 5 && (
                    <p>• {currentData.obesity} casos de obesidad necesitan seguimiento especializado</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
