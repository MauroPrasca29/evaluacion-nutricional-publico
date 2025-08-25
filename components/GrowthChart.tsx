"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import type { Child, ThemeColors } from "@/types"

interface GrowthChartProps {
  child: Child
  theme: ThemeColors
}

export function GrowthChart({ child, theme }: GrowthChartProps) {
  const [isClient, setIsClient] = useState(false)
  const [activeTab, setActiveTab] = useState("weight")

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return (
      <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
        <CardHeader>
          <CardTitle>Gráficos de Crecimiento</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center">
            <p className="text-slate-500">Cargando gráficos...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Datos simulados para el gráfico
  const growthData = {
    weight: [
      { age: 0, value: 3.2, percentile: 50 },
      { age: 6, value: 7.8, percentile: 45 },
      { age: 12, value: 10.2, percentile: 40 },
      { age: 18, value: 12.1, percentile: 35 },
      { age: 24, value: 13.8, percentile: 30 },
    ],
    height: [
      { age: 0, value: 50, percentile: 50 },
      { age: 6, value: 67, percentile: 45 },
      { age: 12, value: 76, percentile: 40 },
      { age: 18, value: 82, percentile: 35 },
      { age: 24, value: 87, percentile: 30 },
    ],
    bmi: [
      { age: 6, value: 17.3, percentile: 50 },
      { age: 12, value: 17.7, percentile: 45 },
      { age: 18, value: 18.0, percentile: 40 },
      { age: 24, value: 18.2, percentile: 35 },
    ],
  }

  const getTrendIcon = (data: any[]) => {
    if (data.length < 2) return <Minus className="w-4 h-4 text-slate-400" />
    const lastTwo = data.slice(-2)
    const trend = lastTwo[1].value - lastTwo[0].value
    if (trend > 0) return <TrendingUp className="w-4 h-4 text-green-500" />
    if (trend < 0) return <TrendingDown className="w-4 h-4 text-red-500" />
    return <Minus className="w-4 h-4 text-slate-400" />
  }

  const getPercentileColor = (percentile: number) => {
    if (percentile < 10) return "bg-red-100 text-red-800"
    if (percentile < 25) return "bg-orange-100 text-orange-800"
    if (percentile < 75) return "bg-green-100 text-green-800"
    if (percentile < 90) return "bg-blue-100 text-blue-800"
    return "bg-purple-100 text-purple-800"
  }

  return (
    <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Gráficos de Crecimiento
          <Badge variant="outline" className="text-xs">
            {child.name}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="weight" className="flex items-center gap-2">
              {getTrendIcon(growthData.weight)}
              Peso
            </TabsTrigger>
            <TabsTrigger value="height" className="flex items-center gap-2">
              {getTrendIcon(growthData.height)}
              Talla
            </TabsTrigger>
            <TabsTrigger value="bmi" className="flex items-center gap-2">
              {getTrendIcon(growthData.bmi)}
              IMC
            </TabsTrigger>
          </TabsList>

          <TabsContent value="weight" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">Evolución del Peso</h3>
              <Badge className={getPercentileColor(growthData.weight[growthData.weight.length - 1].percentile)}>
                Percentil {growthData.weight[growthData.weight.length - 1].percentile}
              </Badge>
            </div>
            <div className="h-64 bg-slate-50 rounded-lg flex items-center justify-center">
              <div className="text-center space-y-2">
                <p className="text-slate-600">Gráfico de Peso vs Edad</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {growthData.weight.map((point, index) => (
                    <div key={index} className="bg-white p-2 rounded border">
                      <div className="font-semibold">{point.age} meses</div>
                      <div className="text-slate-600">{point.value} kg</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="height" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">Evolución de la Talla</h3>
              <Badge className={getPercentileColor(growthData.height[growthData.height.length - 1].percentile)}>
                Percentil {growthData.height[growthData.height.length - 1].percentile}
              </Badge>
            </div>
            <div className="h-64 bg-slate-50 rounded-lg flex items-center justify-center">
              <div className="text-center space-y-2">
                <p className="text-slate-600">Gráfico de Talla vs Edad</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {growthData.height.map((point, index) => (
                    <div key={index} className="bg-white p-2 rounded border">
                      <div className="font-semibold">{point.age} meses</div>
                      <div className="text-slate-600">{point.value} cm</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="bmi" className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-semibold">Evolución del IMC</h3>
              <Badge className={getPercentileColor(growthData.bmi[growthData.bmi.length - 1].percentile)}>
                Percentil {growthData.bmi[growthData.bmi.length - 1].percentile}
              </Badge>
            </div>
            <div className="h-64 bg-slate-50 rounded-lg flex items-center justify-center">
              <div className="text-center space-y-2">
                <p className="text-slate-600">Gráfico de IMC vs Edad</p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {growthData.bmi.map((point, index) => (
                    <div key={index} className="bg-white p-2 rounded border">
                      <div className="font-semibold">{point.age} meses</div>
                      <div className="text-slate-600">{point.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
