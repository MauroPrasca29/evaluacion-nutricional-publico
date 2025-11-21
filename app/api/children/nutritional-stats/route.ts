import { NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/children/nutritional-stats`, {
      headers: {
        "Content-Type": "application/json",
      },
      cache: 'no-store'
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error en proxy /api/children/nutritional-stats:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}