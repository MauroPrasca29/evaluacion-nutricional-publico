"use client"

import { useState } from "react"
import { Upload, FileSpreadsheet, Database, CheckCircle, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { FileUpload } from "./FileUpload"
import type { ThemeColors } from "@/types"

interface ImportDataProps {
  theme: ThemeColors
}

export function ImportData({ theme }: ImportDataProps) {
  const [importFiles, setImportFiles] = useState<File[]>([])
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importResults, setImportResults] = useState<{
    success: number
    errors: number
    warnings: number
    details: string[]
  } | null>(null)

  const handleImport = async () => {
    if (importFiles.length === 0) {
      alert("Por favor selecciona un archivo para importar")
      return
    }

    setImporting(true)
    setImportProgress(0)

    // Simular proceso de importación
    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      setImportProgress(i)
    }

    // Simular resultados
    setImportResults({
      success: 45,
      errors: 2,
      warnings: 3,
      details: [
        "45 registros importados exitosamente",
        "2 registros con errores de formato",
        "3 registros con advertencias menores",
        "Archivo procesado: " + importFiles[0].name,
      ],
    })

    setImporting(false)
  }

  const downloadTemplate = () => {
    // Simular descarga de plantilla
    alert("Descargando plantilla Excel...")
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Importar Datos</h1>
        <p className="text-lg text-slate-600">Importa datos de niños desde archivos Excel o CSV</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Sección de importación */}
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Importar Archivo
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <FileUpload
              id="import-file"
              label="Seleccionar archivo Excel o CSV"
              accept=".xlsx,.xls,.csv"
              multiple={false}
              onFilesChange={setImportFiles}
            />

            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <FileSpreadsheet className="w-4 h-4" />
                <span>Formatos soportados: Excel (.xlsx, .xls), CSV (.csv)</span>
              </div>

              <Button
                variant="outline"
                onClick={downloadTemplate}
                className={`w-full ${theme.cardBorder} hover:bg-opacity-50 bg-transparent`}
              >
                <Download className="w-4 h-4 mr-2" />
                Descargar Plantilla Excel
              </Button>
            </div>

            {importing && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-blue-500 animate-spin" />
                  <span className="text-sm font-medium">Procesando archivo...</span>
                </div>
                <Progress value={importProgress} className="w-full" />
                <p className="text-xs text-slate-500">{importProgress}% completado</p>
              </div>
            )}

            <Button
              onClick={handleImport}
              disabled={importFiles.length === 0 || importing}
              className={`w-full bg-gradient-to-r ${theme.buttonColor} text-white transition-all duration-300 hover:scale-105`}
            >
              {importing ? "Importando..." : "Iniciar Importación"}
            </Button>
          </CardContent>
        </Card>

        {/* Instrucciones */}
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">Instrucciones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">Formato del archivo:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Nombre completo del niño</li>
                <li>• Fecha de nacimiento (DD/MM/AAAA)</li>
                <li>• Género (Masculino/Femenino)</li>
                <li>• Nombre del acudiente</li>
                <li>• Teléfono de contacto</li>
                <li>• Dirección</li>
                <li>• Comunidad</li>
                <li>• Peso actual (kg)</li>
                <li>• Talla actual (cm)</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">Recomendaciones:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Usa la plantilla proporcionada</li>
                <li>• Verifica que no haya celdas vacías</li>
                <li>• Revisa el formato de fechas</li>
                <li>• Máximo 1000 registros por archivo</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Resultados de importación */}
      {importResults && (
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              Resultados de Importación
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{importResults.success}</div>
                <div className="text-sm text-green-700">Exitosos</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{importResults.errors}</div>
                <div className="text-sm text-red-700">Errores</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{importResults.warnings}</div>
                <div className="text-sm text-orange-700">Advertencias</div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-slate-700">Detalles:</h4>
              <ul className="space-y-1">
                {importResults.details.map((detail, index) => (
                  <li key={index} className="text-sm text-slate-600 flex items-center gap-2">
                    <CheckCircle className="w-3 h-3 text-green-500" />
                    {detail}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
