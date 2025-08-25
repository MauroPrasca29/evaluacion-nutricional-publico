"use client"

import { useState, useEffect } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface GrowthData {
  age: number
  weight?: number
  height?: number
  bmi?: number
  date: string
}

interface GrowthChartProps {
  childId: number
  data: GrowthData[]
}

export function GrowthChart({ childId, data }: GrowthChartProps) {
  const [isClient, setIsClient] = useState(false)
  const [activeTab, setActiveTab] = useState("weight")

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient || !data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Gráficos de Crecimiento</CardTitle>
          <CardDescription>Evolución del crecimiento del niño</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-gray-500">
            {!isClient ? "Cargando gráfico..." : "No hay datos disponibles"}
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderChart = (dataKey: string, color: string, label: string, unit: string) => (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="age" label={{ value: "Edad (meses)", position: "insideBottom", offset: -5 }} />
          <YAxis label={{ value: `${label} (${unit})`, angle: -90, position: "insideLeft" }} />
          <Tooltip
            labelFormatter={(value) => `Edad: ${value} meses`}
            formatter={(value: any) => [`${value} ${unit}`, label]}
          />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color, strokeWidth: 2, r: 4 }}
            connectNulls={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gráficos de Crecimiento</CardTitle>
        <CardDescription>Evolución del crecimiento del niño</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="weight">Peso</TabsTrigger>
            <TabsTrigger value="height">Talla</TabsTrigger>
            <TabsTrigger value="bmi">IMC</TabsTrigger>
          </TabsList>

          <TabsContent value="weight" className="mt-4">
            {activeTab === "weight" && renderChart("weight", "#3b82f6", "Peso", "kg")}
          </TabsContent>

          <TabsContent value="height" className="mt-4">
            {activeTab === "height" && renderChart("height", "#10b981", "Talla", "cm")}
          </TabsContent>

          <TabsContent value="bmi" className="mt-4">
            {activeTab === "bmi" && renderChart("bmi", "#f59e0b", "IMC", "kg/m²")}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
