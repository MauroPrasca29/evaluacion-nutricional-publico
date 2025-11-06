"use client"

import { useState } from "react"
import { Upload, FileSpreadsheet, Database, CheckCircle, Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { FileUpload } from "./FileUpload"
import type { ThemeColors } from "@/types"
import * as XLSX from "xlsx";

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
      alert("Por favor selecciona un archivo para importar");
      return;
    }

    setImporting(true);
    setImportProgress(0);

    // Leer el archivo Excel
    const file = importFiles[0];
    const data = await file.arrayBuffer();
    const workbook = XLSX.read(data, { type: "array" });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rows = XLSX.utils.sheet_to_json(sheet, { defval: "" });

    // Validaciones
    const errores: string[] = [];
    let exitosos = 0;

    rows.forEach((row: any, idx: number) => {
      const fila = idx + 2; // +2 por encabezado y base 1
      const celdasConError: string[] = [];

      // Ejemplo de validaciones:
      if (!row["Número de documento"] || typeof row["Número de documento"] !== "string") celdasConError.push(`Número de documento (F${fila})`);
      if (!row["Nombres"] || typeof row["Nombres"] !== "string") celdasConError.push(`Nombres (F${fila})`);
      if (!row["Apellidos"] || typeof row["Apellidos"] !== "string") celdasConError.push(`Apellidos (F${fila})`);
      if (!["Femenino", "Masculino"].includes(row["Género"])) celdasConError.push(`Género (F${fila})`);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(row["Fecha de nacimiento"])) celdasConError.push(`Fecha de nacimiento (F${fila})`);
      if (isNaN(Number(row["Talla (cm)"]))) celdasConError.push(`Talla (cm) (F${fila})`);
      if (isNaN(Number(row["Peso (kg)"]))) celdasConError.push(`Peso (kg) (F${fila})`);
      if (row["Nivel de actividad"] && !["Ligera", "Moderada", "Vigorosa"].includes(row["Nivel de actividad"])) celdasConError.push(`Nivel de actividad (F${fila})`);
      if (row["Tipo de alimentación"] && ![
        "Alimentados con leche materna",
        "Alimentados con fórmula",
        "Alimentados con leche materna + fórmula (todos)",
        "NA"
      ].includes(row["Tipo de alimentación"])) celdasConError.push(`Tipo de alimentación (F${fila})`);

      // Puedes agregar más validaciones según los campos opcionales

      if (celdasConError.length > 0) {
        errores.push(`Fila ${fila}: ${celdasConError.join(", ")}`);
      } else {
        exitosos += 1;
      }
    });

    setImportResults({
      success: exitosos,
      errors: errores.length,
      warnings: 0,
      details: [
        `${exitosos} registros importados exitosamente`,
        `${errores.length} registros con errores de formato`,
        ...errores,
        `Archivo procesado: ${file.name}`,
      ],
    });

    setImporting(false);
  };

  const downloadTemplate = () => {
    // Simular descarga de plantilla
    alert("Descargando plantilla Excel...")
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Importar Datos</h1>
        <p className="text-lg text-slate-600">Importa datos de niños desde archivos Excel</p>
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
              accept=".xlsx,.xls,.csv"
              multiple={false}
              onFilesChange={setImportFiles}
            />

            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <FileSpreadsheet className="w-4 h-4" />
                <span>Formatos soportados: Excel (.xlsx, .xls)</span>
              </div>
              <a
                href="http://localhost:8000/api/import/template"
                target="_blank"
                rel="noopener noreferrer"
                className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-md font-semibold border-2 border-slate-700 text-slate-700 bg-white shadow transition-all duration-300 hover:scale-105 hover:bg-slate-50 hover:shadow-lg`}
                style={{ textDecoration: "none" }}                
              >
                <Download className="w-4 h-4 mr-2" />
                Descargar plantilla Excel
              </a>
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
              <h4 className="font-semibold text-slate-700">Formato del archivo:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Número de documento</li>
                <li>• Nombres</li>
                <li>• Apellidos</li>
                <li>• Género <span className="font-semibold">(selecciona: Femenino o Masculino)</span></li>
                <li>• Fecha de nacimiento (AAAA-MM-DD)</li>
                <li>• Talla (cm)</li>
                <li>• Peso (kg)</li>
                <li>• Pliegue subescapular (mm) - Opcional</li>
                <li>• Perímetro cefálico (cm) - Opcional</li>
                <li>• Pliegue cutáneo tricipital (mm) - Opcional</li>
                <li>• Nivel de actividad <span className="font-semibold">(selecciona: Ligera, Moderada o Vigorosa)</span> - Opcional</li>
                <li>• Tipo de alimentación <span className="font-semibold">(selecciona: Alimentados con leche materna, Alimentados con fórmula, Alimentados con leche materna + fórmula (todos), NA)</span> - Opcional</li>
                <li>• Comentarios del cuidador - Opcional</li>
                <li>• Notas - Opcional</li>
              </ul>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-slate-700">Recomendaciones:</h4>
              <ul className="text-sm text-slate-600 space-y-1 ml-4">
                <li>• Usa la plantilla proporcionada</li>
                <li>• Únicamente se permiten celdas vacías en las columnas opcionales</li>
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
