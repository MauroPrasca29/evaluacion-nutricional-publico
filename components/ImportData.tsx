"use client"

import { useState } from "react"
import { Upload, FileSpreadsheet, Database, CheckCircle, Download, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { FileUpload } from "./FileUpload"
import type { ThemeColors } from "@/types"

interface ImportDataProps {
  theme: ThemeColors
}

interface ImportError {
  fila: number
  infante: string
  errores: string[]
}

interface ImportResult {
  success: boolean
  filename: string
  total_rows: number
  processed_count: number
  error_count: number
  errors: ImportError[]
  data: any[]
}

export function ImportData({ theme }: ImportDataProps) {
  const [importFiles, setImportFiles] = useState<File[]>([])
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importResults, setImportResults] = useState<ImportResult | null>(null)

  const handleImport = async () => {
    if (importFiles.length === 0) {
      alert("Por favor selecciona un archivo para importar");
      return;
    }

    setImporting(true);
    setImportProgress(10);
    setImportResults(null);

    const file = importFiles[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      setImportProgress(30);
      
      const response = await fetch(`/api/import/upload`, {
        method: 'POST',
        body: formData,
      });

      setImportProgress(70);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al procesar el archivo');
      }

      const result: ImportResult = await response.json();
      setImportProgress(100);
      setImportResults(result);

      // Limpiar archivos después de importación exitosa
      if (result.processed_count > 0) {
        setTimeout(() => {
          setImportFiles([]);
        }, 2000);
      }

    } catch (error) {
      console.error('Error al importar:', error);
      alert(`Error al importar: ${error instanceof Error ? error.message : 'Error desconocido'}`);
      setImportProgress(0);
    } finally {
      setImporting(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`/api/import/template`);
      
      if (!response.ok) {
        throw new Error('Error al descargar la plantilla');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'plantilla_importacion_completa.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error al descargar plantilla:', error);
      alert('Error al descargar la plantilla. Verifica que el servidor esté corriendo.');
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Importar Datos</h1>
        <p className="text-lg text-slate-600">Importa datos masivos de infantes, acudientes y seguimientos desde Excel</p>
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
              label="Seleccionar archivo Excel"
              accept=".xlsx,.xls"
              multiple={false}
              onFilesChange={setImportFiles}
            />

            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <FileSpreadsheet className="w-4 h-4" />
                <span>Formatos soportados: Excel (.xlsx, .xls)</span>
              </div>
              <Button
                onClick={downloadTemplate}
                variant="outline"
                className="w-full flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Descargar plantilla Excel
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
              className={`w-full border-2 border-[#357CF6] bg-white text-[#357CF6] font-semibold transition-all duration-300 hover:bg-[#357CF6] hover:text-white hover:scale-105`}
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
              <h4 className="font-semibold text-slate-700">El archivo debe contener:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• <strong>Datos del Infante:</strong> nombre, fecha de nacimiento, género, sede</li>
                <li>• <strong>Datos del Acudiente:</strong> nombre, teléfono, documento</li>
                <li>• <strong>Datos del Seguimiento:</strong> fecha, peso, estatura</li>
                <li>• <strong>Medidas Opcionales:</strong> perímetro cefálico, pliegues, circunferencias</li>
                <li>• <strong>Nivel de actividad:</strong> Ligera, Moderada, Intensa</li>
                <li>• <strong>Tipo de alimentación:</strong> Lactancia materna, Fórmula, Mixta</li>
                <li>• <strong>Exámenes:</strong> hemoglobina (opcional)</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">El sistema automáticamente:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Crea o busca acudientes existentes</li>
                <li>• Crea o busca infantes existentes</li>
                <li>• Genera seguimientos con evaluación nutricional completa</li>
                <li>• Calcula z-scores y clasificaciones según OMS</li>
                <li>• Genera recomendaciones nutricionales personalizadas</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">Recomendaciones:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Descarga y usa la plantilla proporcionada</li>
                <li>• Las listas desplegables tienen los valores correctos</li>
                <li>• Fechas en formato YYYY-MM-DD</li>
                <li>• Revisa los errores antes de reintentar</li>
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
              {importResults.processed_count > 0 ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500" />
              )}
              Resultados de Importación
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{importResults.total_rows}</div>
                <div className="text-sm text-blue-700">Total Filas</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{importResults.processed_count}</div>
                <div className="text-sm text-green-700">Exitosos</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{importResults.error_count}</div>
                <div className="text-sm text-red-700">Errores</div>
              </div>
            </div>

            {importResults.processed_count > 0 && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">✓ Importación exitosa</h4>
                <p className="text-sm text-green-700">
                  Se procesaron {importResults.processed_count} registros correctamente con evaluaciones nutricionales completas.
                </p>
              </div>
            )}

            {importResults.error_count > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-red-700">Errores encontrados:</h4>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {importResults.errors.map((error, index) => (
                    <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="font-semibold text-red-800">
                        Fila {error.fila} - {error.infante}
                      </div>
                      <ul className="mt-1 ml-4 space-y-1">
                        {error.errores.map((err, errIdx) => (
                          <li key={errIdx} className="text-sm text-red-600">
                            • {err}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}