import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    
    const response = await fetch(`${BACKEND_BASE}/api/import/upload`, {
      method: "POST",
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error en proxy /api/import/upload:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}