import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const indicator = searchParams.get('indicator')
    const age_days = searchParams.get('age_days')
    const gender = searchParams.get('gender')
    const value = searchParams.get('value')

    const params = new URLSearchParams({
      indicator: indicator || '',
      age_days: age_days || '',
      gender: gender || '',
      value: value || ''
    })

    const response = await fetch(
      `${BACKEND_BASE}/api/nutrition/growth-chart-data?${params.toString()}`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    )

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error en proxy /api/nutrition/growth-chart-data:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}