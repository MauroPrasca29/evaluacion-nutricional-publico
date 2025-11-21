// app/api/auth-login/route.ts
import { NextResponse } from 'next/server'

const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

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
