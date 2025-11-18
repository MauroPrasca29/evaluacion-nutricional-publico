import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/import/template`)

    if (!response.ok) {
      return new NextResponse("Error al generar la plantilla", { status: response.status })
    }

    const blob = await response.blob()
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": "attachment; filename=plantilla_importacion_completa.xlsx"
      }
    })
  } catch (error) {
    console.error("Error en proxy /api/import/template:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}