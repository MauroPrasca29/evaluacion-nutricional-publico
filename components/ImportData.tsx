// components/ImportData.tsx - Versión con debugging extremo
"use client"

import { useState, useEffect, useRef } from "react"
import { Upload, FileSpreadsheet, Database, CheckCircle, Download, AlertCircle, Clock } from "lucide-react"
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
  filename?: string
  total_rows: number
  processed_count: number
  error_count: number
  errors: ImportError[]
  data: any[]
  processing_time?: number
  detail?: string
}

export function ImportData({ theme }: ImportDataProps) {
  const [importFiles, setImportFiles] = useState<File[]>([])
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importResults, setImportResults] = useState<ImportResult | null>(null)
  const [estimatedTime, setEstimatedTime] = useState<string>("")
  const [elapsedTime, setElapsedTime] = useState<number>(0)
  const [currentPhase, setCurrentPhase] = useState<string>("")
  const [debugLogs, setDebugLogs] = useState<string[]>([])
  const startTimeRef = useRef<number>(0)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const addLog = (message: string) => {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0]
    const logMessage = `[${timestamp}] ${message}`
    console.log(logMessage)
    setDebugLogs(prev => [...prev.slice(-20), logMessage]) // Mantener últimos 20 logs
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current)
    }
  }, [])

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}m ${secs}s`
  }

  const testBackendConnection = async () => {
    try {
      addLog("🔍 Probando conexión con backend...")
      const response = await fetch('/api/import/template', { method: 'GET' })
      if (response.ok) {
        addLog("✅ Backend responde correctamente")
        return true
      } else {
        addLog(`❌ Backend respondió con status ${response.status}`)
        return false
      }
    } catch (error) {
      addLog(`❌ Error conectando con backend: ${error}`)
      return false
    }
  }

  const handleImport = async () => {
    if (importFiles.length === 0) {
      alert("Por favor selecciona un archivo para importar")
      return
    }

    // Test de conexión previo
    const backendOk = await testBackendConnection()
    if (!backendOk) {
      alert("⚠️ El backend no responde. Verifica que el servidor esté corriendo en el puerto 8000.")
      return
    }

    setImporting(true)
    setImportProgress(0)
    setImportResults(null)
    setElapsedTime(0)
    setCurrentPhase("Iniciando...")
    setDebugLogs([])

    const file = importFiles[0]
    const formData = new FormData()
    formData.append('file', file)

    startTimeRef.current = Date.now()
    
    // Timer para tiempo transcurrido
    timerRef.current = setInterval(() => {
      setElapsedTime((Date.now() - startTimeRef.current) / 1000)
    }, 100)

    // Estimación
    const fileSizeMB = file.size / (1024 * 1024)
    const estimatedSeconds = Math.max(10, Math.ceil(fileSizeMB * 2))
    setEstimatedTime(`Estimado: ${formatTime(estimatedSeconds)}`)
    
    addLog(`📤 Iniciando importación: ${file.name} (${fileSizeMB.toFixed(2)} MB)`)
    addLog(`⏱️ Tiempo estimado: ${estimatedSeconds}s`)

    try {
      // Progreso simulado
      let currentProgress = 0
      progressIntervalRef.current = setInterval(() => {
        const elapsed = (Date.now() - startTimeRef.current) / 1000
        
        if (elapsed < estimatedSeconds * 0.1) {
          currentProgress = 5 + (15 * (elapsed / (estimatedSeconds * 0.1)))
          setCurrentPhase("📋 Validando archivo...")
        } else if (elapsed < estimatedSeconds * 0.7) {
          const progress = (elapsed - estimatedSeconds * 0.1) / (estimatedSeconds * 0.6)
          currentProgress = 20 + (60 * progress)
          setCurrentPhase("⚙️ Procesando en lote...")
        } else {
          const progress = (elapsed - estimatedSeconds * 0.7) / (estimatedSeconds * 0.3)
          currentProgress = 80 + (15 * Math.min(progress, 1))
          setCurrentPhase("💾 Guardando...")
        }
        
        setImportProgress(Math.min(currentProgress, 95))
      }, 300)
      
      addLog("🔄 Enviando request a /api/import/upload...")
      
      const controller = new AbortController()
      const timeoutId = setTimeout(() => {
        addLog("⏰ Timeout de 10 minutos alcanzado - abortando")
        controller.abort()
      }, 600000)
      
      const fetchStart = Date.now()
      const response = await fetch(`/api/import/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      })

      const fetchTime = ((Date.now() - fetchStart) / 1000).toFixed(2)
      addLog(`📡 Response recibida en ${fetchTime}s - Status: ${response.status}`)

      clearTimeout(timeoutId)
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }

      setImportProgress(96)
      setCurrentPhase("🔍 Procesando respuesta...")

      // Verificar headers
      const contentType = response.headers.get('content-type')
      const contentLength = response.headers.get('content-length')
      addLog(`📋 Content-Type: ${contentType || 'null'}`)
      addLog(`📏 Content-Length: ${contentLength || 'null'}`)

      // Leer el body como text primero
      const text = await response.text()
      addLog(`📝 Response length: ${text.length} caracteres`)
      
      if (text.length > 0) {
        addLog(`📄 Primeros 200 chars: ${text.substring(0, 200)}`)
      } else {
        addLog(`❌ Response VACÍA - El backend no devolvió nada`)
        throw new Error('El backend devolvió una respuesta vacía. Verifica los logs del servidor.')
      }

      if (!contentType?.includes('application/json')) {
        addLog(`❌ Content-Type no es JSON: ${contentType}`)
        addLog(`❌ Response completa: ${text}`)
        throw new Error(`El servidor respondió con ${contentType || 'sin content-type'} en lugar de JSON`)
      }

      let result: ImportResult
      try {
        result = JSON.parse(text)
        addLog(`✅ JSON parseado correctamente`)
        addLog(`📊 Resultado: ${result.processed_count || 0} procesados, ${result.error_count || 0} errores`)
      } catch (parseError) {
        addLog(`❌ Error parseando JSON: ${parseError}`)
        addLog(`❌ Text que intentó parsear: ${text.substring(0, 500)}`)
        throw new Error('Error al parsear JSON del servidor')
      }

      if (!response.ok) {
        addLog(`⚠️ Response no OK (${response.status}): ${result.detail || 'sin detalle'}`)
        throw new Error(result.detail || `Error HTTP ${response.status}`)
      }

      const totalTime = (Date.now() - startTimeRef.current) / 1000
      result.processing_time = result.processing_time || totalTime
      
      addLog(`🎉 Importación completada exitosamente`)
      addLog(`📊 ${result.processed_count} registros en ${formatTime(totalTime)}`)
      
      setImportProgress(100)
      setImportResults(result)
      setEstimatedTime(`Completado en ${formatTime(totalTime)}`)
      setCurrentPhase("✅ Completado")
      setElapsedTime(totalTime)

      if (result.processed_count > 0) {
        setTimeout(() => setImportFiles([]), 2000)
      }

    } catch (error) {
      if (timerRef.current) clearInterval(timerRef.current)
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current)
      
      addLog(`❌ ERROR: ${error}`)
      
      let errorMessage = 'Error desconocido'
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = '⏰ La importación tardó más de 10 minutos.\n\nRecomendaciones:\n• Divide el archivo en partes más pequeñas (máximo 200-300 filas)\n• Verifica que el servidor backend esté corriendo\n• Revisa los logs del backend para ver si hay errores'
        } else {
          errorMessage = error.message
        }
      }
      
      alert(`❌ Error al importar:\n\n${errorMessage}\n\n🔍 Revisa los logs de debugging más abajo para más detalles.`)
      setImportProgress(0)
      setEstimatedTime("")
      setCurrentPhase("")
      setElapsedTime(0)
    } finally {
      setImporting(false)
    }
  }

  const downloadTemplate = async () => {
    try {
      const response = await fetch(`/api/import/template`)
      if (!response.ok) throw new Error('Error al descargar la plantilla')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'plantilla_importacion_completa.xlsx'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error al descargar plantilla:', error)
      alert('Error al descargar la plantilla.')
    }
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Importar Datos</h1>
        <p className="text-lg text-slate-600">Importa datos masivos de infantes, acudientes y seguimientos desde Excel</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg}`}>
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
                <span>Formatos: Excel (.xlsx, .xls)</span>
              </div>
              <Button onClick={downloadTemplate} variant="outline" className="w-full flex items-center justify-center gap-2">
                <Download className="w-4 h-4" />
                Descargar plantilla Excel
              </Button>
            </div>

            {importing && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-blue-500 animate-spin" />
                    <span className="text-sm font-medium">{currentPhase}</span>
                  </div>
                  <div className="flex items-center gap-1 text-blue-600">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm font-semibold">{formatTime(elapsedTime)}</span>
                  </div>
                </div>
                
                <Progress value={importProgress} className="w-full h-3" />
                
                <div className="flex justify-between items-center">
                  <p className="text-sm text-slate-600 font-medium">{Math.round(importProgress)}%</p>
                  <p className="text-xs text-blue-500 font-medium">{estimatedTime}</p>
                </div>
                
                {elapsedTime > 30 && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <p className="text-xs text-amber-700">
                      ⏳ Procesamiento largo detectado. No cierres esta ventana.
                    </p>
                  </div>
                )}
              </div>
            )}

            <Button
              onClick={handleImport}
              disabled={importFiles.length === 0 || importing}
              className="w-full border-2 border-[#357CF6] bg-white text-[#357CF6] font-semibold hover:bg-[#357CF6] hover:text-white disabled:opacity-50"
            >
              {importing ? "Importando..." : "Iniciar Importación"}
            </Button>
          </CardContent>
        </Card>

        {/* Instrucciones */}
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800">⚙️ Instrucciones & Rendimiento</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">⚡ Optimizaciones Activas:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• <strong>Batch Processing:</strong> 90% más rápido</li>
                <li>• <strong>Cache WHO/RIEN:</strong> Tablas en memoria</li>
                <li>• <strong>Bulk Inserts:</strong> Menos queries a DB</li>
                <li>• <strong>~100 seguimientos:</strong> 20-30 segundos</li>
                <li>• <strong>~500 seguimientos:</strong> 2-4 minutos</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">📋 Recomendaciones:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Descarga la plantilla Excel</li>
                <li>• Máximo 300-500 filas por archivo</li>
                <li>• Fechas en formato YYYY-MM-DD</li>
                <li>• Verifica que el backend esté corriendo</li>
              </ul>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-700 font-medium">
                💡 Si ves "Respuesta vacía", verifica que el servidor backend esté corriendo en el puerto 8000
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Debug Logs */}
      {debugLogs.length > 0 && (
        <Card className="bg-slate-900 text-green-400 border-slate-700">
          <CardHeader>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              🔍 Logs de Debugging (últimos 20)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-xs space-y-1 max-h-64 overflow-y-auto">
              {debugLogs.map((log, idx) => (
                <div key={idx} className="whitespace-pre-wrap break-all">
                  {log}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resultados */}
      {importResults && (
        <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50`}>
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
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-2xl font-bold text-purple-600">
                  <Clock className="w-5 h-5" />
                  {importResults.processing_time ? formatTime(importResults.processing_time) : formatTime(elapsedTime)}
                </div>
                <div className="text-sm text-purple-700">Tiempo Total</div>
              </div>
            </div>

            {importResults.processed_count > 0 && importResults.processing_time && (
              <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">⚡ Estadísticas de Rendimiento</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-slate-600">Velocidad:</span>
                    <span className="ml-2 font-semibold text-blue-700">
                      {(importResults.processed_count / importResults.processing_time).toFixed(1)} reg/seg
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-600">Promedio:</span>
                    <span className="ml-2 font-semibold text-blue-700">
                      {((importResults.processing_time / importResults.processed_count) * 1000).toFixed(0)} ms/reg
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-600">Eficiencia:</span>
                    <span className="ml-2 font-semibold text-green-700">
                      {((importResults.processed_count / importResults.total_rows) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {importResults.processed_count > 0 && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">✓ Importación exitosa</h4>
                <p className="text-sm text-green-700">
                  Se procesaron <strong>{importResults.processed_count}</strong> registros en {formatTime(importResults.processing_time || elapsedTime)}.
                </p>
              </div>
            )}

            {importResults.error_count > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-red-700">Errores ({importResults.error_count}):</h4>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {importResults.errors.map((error, index) => (
                    <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="font-semibold text-red-800">
                        Fila {error.fila} - {error.infante}
                      </div>
                      <ul className="mt-1 ml-4 space-y-1">
                        {error.errores.map((err, errIdx) => (
                          <li key={errIdx} className="text-sm text-red-600">• {err}</li>
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