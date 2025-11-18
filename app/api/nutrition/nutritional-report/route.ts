import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams

    const response = await fetch(
      `${BACKEND_BASE}/api/nutrition/nutritional-report?${searchParams.toString()}`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    )

    if (!response.ok) {
      return new NextResponse("Error al generar el reporte", { status: response.status })
    }

    // Para PDFs, devolver el blob directamente
    const blob = await response.blob()
    return new NextResponse(blob, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="reporte_nutricional.pdf"`
      }
    })
  } catch (error) {
    console.error("Error en proxy /api/nutrition/nutritional-report:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}