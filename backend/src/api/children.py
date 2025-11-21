// app/api/children/alerts/count/route.ts
import { NextResponse } from "next/server"

// 👉 URL base del backend en Railway
const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/children/alerts/count`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      // Si en el futuro este endpoint requiere auth por cookie, credentials: "include"
      // credentials: "include",
    })

    if (!response.ok) {
      // Si el backend falla, devolvemos 0 pero no rompemos el dashboard
      return NextResponse.json({ count: 0 }, { status: 200 })
    }

    const data = await response.json()
    // Backend ya devuelve { "count": n }, lo mandamos tal cual
    return NextResponse.json(data, { status: 200 })
  } catch (error) {
    console.error("Error in alerts count route:", error)
    return NextResponse.json({ count: 0 }, { status: 200 })
  }
}
