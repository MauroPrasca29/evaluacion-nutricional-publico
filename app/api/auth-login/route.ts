// app/api/auth-login/route.ts
import { NextResponse } from 'next/server'

// PRIORIDAD:
// 1) BACKEND_BASE   → variable privada del servidor en Vercel
// 2) NEXT_PUBLIC_API_URL → variable pública del frontend (también válida en SSR)
// 3) localhost para desarrollo local
const BACKEND_BASE =
  process.env.BACKEND_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000"

export async function POST(request: Request) {
  try {
    const body = await request.json()

    console.log(`🔄 [Auth-Login] Proxy → ${BACKEND_BASE}/api/auth/login`)

    const response = await fetch(`${BACKEND_BASE}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    })

    // === Leemos texto primero para evitar errores si viene vacío
    const text = await response.text()
    let data: any = {}

    try {
      data = text ? JSON.parse(text) : {}
    } catch (parseError) {
      console.error("❌ [Auth-Login] Error parseando JSON:", parseError)
      console.error("Respuesta cruda:", text)
    }

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true',
      },
    })
  } catch (error: any) {
    console.error("❌ [Auth-Login Error]:", error)

    return new Response(
      JSON.stringify({
        detail: "Error en login",
        error: error?.message || "Error desconocido",
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}

// Preflight CORS para navegadores
export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}
