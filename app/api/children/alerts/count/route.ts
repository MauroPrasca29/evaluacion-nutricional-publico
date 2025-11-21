import { NextResponse } from "next/server"

const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/children/alerts/count`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      // Si falla el backend, devolvemos 0 para no romper el dashboard
      return NextResponse.json({ count: 0 }, { status: 200 })
    }

    const data = await response.json()
    // Backend ya devuelve { "count": n }
    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    console.error("Error in alerts count route:", error)
    return NextResponse.json({ count: 0 }, { status: 200 })
  }
}
