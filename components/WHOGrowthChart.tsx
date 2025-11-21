// components/WHOGrowthChart.tsx
"use client"

import { useMemo, memo, useState, useEffect } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Scatter, ComposedChart, ReferenceLine } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from 'lucide-react'

interface Seguimiento {
  id_seguimiento: number
  fecha: string
  peso?: number
  estatura?: number
  imc?: number
  perimetro_cefalico?: number
  pliegue_triceps?: number
  pliegue_subescapular?: number
  circunferencia_braquial?: number
  perimetro_abdominal?: number
}

interface WHOGrowthChartProps {
  // Props existentes para un solo punto
  data?: {
    indicator: string
    indicator_name: string
    gender: string
    child_age_months: number
    child_value: number
    chart_data: Array<{
      age: number
      p3: number
      p15: number
      p50: number
      p85: number
      p97: number
    }>
  }
  // Nuevas props para múltiples puntos
  chartType?: 'weight' | 'height' | 'bmi' | 'head_circumference' | 'triceps_skinfold' | 'subscapular_skinfold' | 'arm_circumference' | 'abdominal_perimeter'
  gender?: 'male' | 'female'
  seguimientos?: Seguimiento[]
  childBirthDate?: string
}

const CHART_LABELS = {
  weight: 'Peso',
  height: 'Talla',
  bmi: 'IMC',
  head_circumference: 'Perímetro Cefálico',
  triceps_skinfold: 'Pliegue Tricipital',
  subscapular_skinfold: 'Pliegue Subescapular',
  arm_circumference: 'Circunferencia Braquial',
  abdominal_perimeter: 'Perímetro Abdominal'
}

const SEGUIMIENTO_FIELD_MAP: Record<string, keyof Seguimiento> = {
  weight: 'peso',
  height: 'estatura',
  bmi: 'imc',
  head_circumference: 'perimetro_cefalico',
  triceps_skinfold: 'pliegue_triceps',
  subscapular_skinfold: 'pliegue_subescapular',
  arm_circumference: 'circunferencia_braquial',
  abdominal_perimeter: 'perimetro_abdominal'
}

const INDICATOR_BACKEND_MAP: Record<string, string> = {
  weight: 'peso',
  height: 'talla',
  bmi: 'imc',
  head_circumference: 'perimetro_cefalico',
  triceps_skinfold: 'pliegue_triceps',
  subscapular_skinfold: 'pliegue_subescapular',
  arm_circumference: 'circunferencia_braquial',
  abdominal_perimeter: 'perimetro_abdominal'
}

// Memoizar el tooltip para evitar re-renders innecesarios
const CustomTooltip = memo(({ active, payload }: any) => {
  if (!active || !payload || !payload.length) return null
  
  const data = payload[0].payload
  
  // Si es el punto del niño (múltiples puntos históricos)
  if (data.childValue !== undefined && data.childValue !== null) {
    return (
      <div className="bg-blue-600 text-white p-3 border-2 border-white rounded-lg shadow-lg">
        <p className="text-sm font-bold">Medición</p>
        <p className="text-xs">Edad: {data.age.toFixed(0)} meses</p>
        <p className="text-xs">Valor: {data.childValue.toFixed(2)}</p>
        {data.fecha && <p className="text-xs mt-1">Fecha: {data.fecha}</p>}
      </div>
    )
  }
  
  // Tooltips normales para las curvas
  return (
    <div className="bg-white p-3 border border-slate-200 rounded-lg shadow-lg">
      <p className="text-sm font-semibold mb-2">
        Edad: {data.age.toFixed(0)} meses
      </p>
      {data.p3 && <p className="text-xs text-red-500">P3: {data.p3.toFixed(2)}</p>}
      {data.p15 && <p className="text-xs text-orange-500">P15: {data.p15.toFixed(2)}</p>}
      {data.p50 && <p className="text-xs text-green-600">P50: {data.p50.toFixed(2)}</p>}
      {data.p85 && <p className="text-xs text-orange-500">P85: {data.p85.toFixed(2)}</p>}
      {data.p97 && <p className="text-xs text-red-500">P97: {data.p97.toFixed(2)}</p>}
    </div>
  )
})

CustomTooltip.displayName = 'CustomTooltip'

const CustomXAxisTick = memo(({ x, y, payload }: any) => {
  const value = payload.value
  const years = Math.floor(value / 12)
  const months = Math.round(value % 12)
  
  let text = ''
  let isBold = false
  let dyOffset = 16  // Default para meses
  
  if (value === 0) {
    text = 'Nacimiento'
    dyOffset = 30  // Mismo nivel que años
  } else if (value % 12 === 0 && value > 0) {
    text = `${years} año${years !== 1 ? 's' : ''}`
    isBold = true
    dyOffset = 30  // Más abajo para años
  } else if (months > 0) {
    text = `${months}`
    dyOffset = 16  // Arriba para meses
  }
  
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={dyOffset}
        textAnchor="middle"
        fill="#666"
        fontSize={11}
        fontWeight={isBold ? 'bold' : 'normal'}
      >
        {text}
      </text>
    </g>
  )
})

CustomXAxisTick.displayName = 'CustomXAxisTick'

export const WHOGrowthChart = memo(({ data, chartType, gender, seguimientos, childBirthDate }: WHOGrowthChartProps) => {
  const [chartData, setChartData] = useState<any>(null)
  const [loading, setLoading] = useState(false)


  // Calcular edad en meses desde fecha de nacimiento
  const calculateAgeInMonths = (birthDate: string, measurementDate: string): number => {
    const birth = new Date(birthDate)
    const measurement = new Date(measurementDate)
    const months = (measurement.getFullYear() - birth.getFullYear()) * 12 + (measurement.getMonth() - birth.getMonth())
    const days = measurement.getDate() - birth.getDate()
    return months + (days / 30.44) // Promedio de días por mes
  }

  // Cargar datos de gráfica WHO si se usan seguimientos múltiples
  useEffect(() => {
    if (!chartType || !gender || !seguimientos || !childBirthDate || seguimientos.length === 0) return

    const loadChartData = async () => {
      setLoading(true)
      try {
        // Usar el seguimiento más reciente para obtener edad y valor
        const latestSeguimiento = seguimientos[seguimientos.length - 1]
        const ageInMonths = calculateAgeInMonths(childBirthDate, latestSeguimiento.fecha)
        const ageDays = Math.floor(ageInMonths * 30.44)
        
        // Obtener el valor del campo correspondiente
        const fieldName = SEGUIMIENTO_FIELD_MAP[chartType]
        const fieldValue = latestSeguimiento[fieldName]
        
        // Si no hay valor para este indicador, no cargar la gráfica
        if (!fieldValue || fieldValue === 0) {
          setChartData(null)
          setLoading(false)
          return
        }
        
        // Usar el nombre del indicador en español para el backend
        const indicatorBackend = INDICATOR_BACKEND_MAP[chartType]
        
        const response = await fetch(
          `/api/nutrition/growth-chart-data?indicator=${indicatorBackend}&age_days=${ageDays}&gender=${gender}&value=${fieldValue}`
        )
        
        if (response.ok) {
          const whoData = await response.json()
          setChartData(whoData)
        } else {
          const errorText = await response.text()
          console.error(`Error cargando datos WHO para ${chartType}:`, response.status, errorText)
          setChartData(null)
        }
      } catch (error) {
        console.error("Error cargando datos de gráfica WHO:", error)
        setChartData(null)
      } finally {
        setLoading(false)
      }
    }

    loadChartData()
    }, [chartType, gender, seguimientos, childBirthDate])

  // Procesar datos para el gráfico
  const processedData = useMemo(() => {
    // Modo antiguo: un solo punto
    if (data) {
      const baseData = data.chart_data.length > 100 
        ? data.chart_data.filter((_, index) => index % 2 === 0) 
        : data.chart_data
      
      return [
        ...baseData,
        {
          age: data.child_age_months,
          p3: null,
          p15: null,
          p50: null,
          p85: null,
          p97: null,
          childValue: data.child_value
        }
      ]
    }

    // Modo nuevo: múltiples puntos históricos
    if (chartData && seguimientos && childBirthDate) {
    console.log("🔍 DEBUG Chart Type:", chartType)
    console.log("🔍 Seguimientos recibidos:", seguimientos)
    console.log("🔍 ChartData:", chartData)
    
    const baseData = chartData.chart_data.length > 100 
      ? chartData.chart_data.filter((_: any, index: number) => index % 2 === 0) 
      : chartData.chart_data

    const fieldName = SEGUIMIENTO_FIELD_MAP[chartType!]
    console.log("🔍 Field name a buscar:", fieldName)
    
    // Agregar todos los puntos del seguimiento que tengan valor
    const childPoints = seguimientos
      .filter((seg: any) => {
        const hasValue = seg[fieldName] != null && seg[fieldName] > 0
        console.log(`🔍 Seguimiento ${seg.id_seguimiento}: ${fieldName} = ${seg[fieldName]}, hasValue: ${hasValue}`)
        return hasValue
      })
      .map((seg: any) => ({
        age: calculateAgeInMonths(childBirthDate, seg.fecha),
        p3: null,
        p15: null,
        p50: null,
        p85: null,
        p97: null,
        childValue: seg[fieldName],
        fecha: new Date(seg.fecha).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' }),
        seguimientoId: seg.id_seguimiento
      }))
      .sort((a, b) => a.age - b.age) // Ordenar por edad

    console.log("🔍 Child points generados:", childPoints)
    console.log("🔍 Datos finales (base + points):", [...baseData, ...childPoints])
    
    return [...baseData, ...childPoints]
  }

    return []
  }, [data, chartData, seguimientos, childBirthDate, chartType])

  // Obtener el rango de edad de los datos
  const ageRange = useMemo(() => {
    const sourceData = data?.chart_data || chartData?.chart_data || []
    if (sourceData.length === 0) return [0, 60]
    const minAge = Math.min(...sourceData.map((d: any) => d.age))
    const maxAge = Math.max(...sourceData.map((d: any) => d.age))
    return [Math.floor(minAge), Math.ceil(maxAge)]
  }, [data, chartData])

  const customTicks = useMemo(() => {
    const [minAge, maxAge] = ageRange
    const ticks = [0] // Nacimiento
    
    // Para cada año hasta el máximo, agregar meses de 2 en 2, incluyendo 10
    const maxYears = Math.ceil(maxAge / 12)
    
    for (let year = 0; year < maxYears; year++) {
      for (let month = 2; month <= 10; month += 2) {  // Cambiar <= 12 por <= 10
        const totalMonths = year * 12 + month
        if (totalMonths <= maxAge) {
          ticks.push(totalMonths)
        }
      }
      // Agregar el año completo (mes 12)
      const yearComplete = (year + 1) * 12
      if (yearComplete <= maxAge) {
        ticks.push(yearComplete)
      }
    }
    
    return ticks.sort((a, b) => a - b)
  }, [ageRange])

  const xAxisFormatter = useMemo(() => (value: number) => {
    const years = Math.floor(value / 12)
    const months = Math.round(value % 12)
    
    if (value === 0) return 'Nacimiento'
    
    // Si es un año completo (múltiplo de 12)
    if (value % 12 === 0 && value > 0) {
      return `${years} año${years !== 1 ? 's' : ''}`
    }
    
    // Para todos los meses (incluyendo después del primer año)
    if (months > 0) {
      return `${months}`
    }
    
    return ''
}, [])

  // Determinar el nombre del indicador
  const indicatorName = data?.indicator_name || (chartType ? CHART_LABELS[chartType] : '')

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-bold text-slate-800">
            {indicatorName} para la Edad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-slate-600">Cargando gráfica...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (processedData.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-bold text-slate-800">
            {indicatorName} para la Edad
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center">
            <p className="text-slate-500">No hay datos disponibles para esta medición</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg font-bold text-slate-800">
          {indicatorName} para la Edad
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart 
              data={processedData}
              margin={{ top: 10, right: 30, left: 20, bottom: 50 }}  // Aumentar de 20 a 50
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              {/* Líneas verticales más gruesas para cada año */}
              {customTicks.filter(tick => tick % 12 === 0 && tick > 0).map(tick => (
                <ReferenceLine 
                  key={`year-${tick}`}
                  x={tick} 
                  stroke="#cbd5e1" 
                  strokeWidth={1.5}
                />
              ))}
              <XAxis 
                dataKey="age" 
                label={{ value: "Edad (en meses y años cumplidos)", position: "insideBottom", offset: -35 }}
                tick={<CustomXAxisTick />}
                domain={ageRange}
                type="number"
                allowDataOverflow={false}
                ticks={customTicks}
              />
              <YAxis 
                label={{ value: indicatorName, angle: -90, position: "insideLeft", style: { textAnchor: 'middle' } }}
                tick={{ fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="top" 
                height={36}
                wrapperStyle={{ fontSize: '12px' }}
                iconType="line"
              />
              
              {/* Curvas de percentiles */}
              <Line 
                type="monotone" 
                dataKey="p3" 
                stroke="#ef4444" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false} 
                name="P3"
                isAnimationActive={false}
                connectNulls={true}
              />
              <Line 
                type="monotone" 
                dataKey="p15" 
                stroke="#f59e0b" 
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={false} 
                name="P15"
                isAnimationActive={false}
                connectNulls={true}
              />
              <Line 
                type="monotone" 
                dataKey="p50" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={false} 
                name="P50 (Mediana)"
                isAnimationActive={false}
                connectNulls={true}
              />
              <Line 
                type="monotone" 
                dataKey="p85" 
                stroke="#f59e0b" 
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={false} 
                name="P85"
                isAnimationActive={false}
                connectNulls={true}
              />
              <Line 
                type="monotone" 
                dataKey="p97" 
                stroke="#ef4444" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false} 
                name="P97"
                isAnimationActive={false}
                connectNulls={true}
              />
              
              {/* Puntos del niño - conectados con línea para mostrar progreso */}
              <Line 
                type="monotone"
                dataKey="childValue"  
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{
                  r: 3,  // Puntos más pequeños
                  fill: "#3b82f6",
                  stroke: "#fff",
                  strokeWidth: 0.5  // Borde muy fino
                }}
                name={seguimientos && seguimientos.length > 1 ? "Seguimientos" : "Medición actual"}
                isAnimationActive={false}
                connectNulls={true}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
})

WHOGrowthChart.displayName = 'WHOGrowthChart'