import { NextResponse } from 'next/server'

const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_BASE}/api/children/alerts/count`, {
      headers: {
        'Content-Type': 'application/json',
      },
      // 🚨 Importante: mantener credenciales para sesiones auth
      credentials: "include",
    })

    if (!response.ok) {
      return NextResponse.json({ count: 0 }, { status: 200 })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in alerts count route:', error)
    return NextResponse.json({ count: 0 }, { status: 200 })
  }
}
