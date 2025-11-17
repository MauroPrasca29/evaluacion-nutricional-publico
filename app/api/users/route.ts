import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.BACKEND_BASE || "http://localhost:8000"

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")
    
    if (!authHeader) {
      return NextResponse.json(
        { detail: "No autorizado" },
        { status: 401 }
      )
    }

    // Obtener parámetros de query
    const { searchParams } = new URL(request.url)
    const skip = searchParams.get("skip") || "0"
    const limit = searchParams.get("limit") || "100"

    const response = await fetch(`${BACKEND_BASE}/api/auth/users?skip=${skip}&limit=${limit}`, {
      headers: {
        "Authorization": authHeader,
      },
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error en proxy /api/users:", error)
    return NextResponse.json(
      { detail: "Error del servidor" },
      { status: 500 }
    )
  }
}
