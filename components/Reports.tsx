import { FileText, Upload, PieChart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ThemeColors } from "@/types"

interface ReportsProps {
  theme: ThemeColors
}

export function Reports({ theme }: ReportsProps) {
  return (
    <div className="space-y-6">
      <div
        className={`bg-gradient-to-r ${theme.cardBg} rounded-xl p-6 border ${theme.cardBorder} transition-all duration-500`}
      >
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Reportes y Estadísticas</h1>
        <p className="text-slate-600">Análisis del estado nutricional infantil</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card
          className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500 hover:scale-105`}
        >
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <PieChart className={`w-5 h-5 ${theme.accentColor}`} />
              Estado Nutricional
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="font-medium text-slate-700">Normal</span>
              <span className="font-bold text-slate-800">118 (75.6%)</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
              <span className="font-medium text-slate-700">Alerta</span>
              <span className="font-bold text-slate-800">28 (17.9%)</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="font-medium text-slate-700">Seguimiento</span>
              <span className="font-bold text-slate-800">10 (6.4%)</span>
            </div>
          </CardContent>
        </Card>

        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Exportar Reportes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              variant="outline"
              className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
            >
              <FileText className="w-4 h-4 mr-2" />
              Exportar PDF
            </Button>
            <Button
              variant="outline"
              className={`${theme.cardBorder} w-full hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105`}
            >
              <Upload className="w-4 h-4 mr-2" />
              Exportar Excel
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
