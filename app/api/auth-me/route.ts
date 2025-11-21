// app/api/auth-me/route.ts

const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    console.log(`🔄 [Auth-Me] Proxy → ${BACKEND_BASE}/api/auth/me`)

    const response = await fetch(`${BACKEND_BASE}/api/auth/me`, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    })

    const text = await response.text()
    let data: any = {}

    try {
      data = text ? JSON.parse(text) : {}
    } catch (err) {
      console.error("❌ [Auth-Me] Error parseando JSON:", err, text)
    }

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
  } catch (error: any) {
    console.error("❌ [Auth-Me Error]:", error)
    return new Response(
      JSON.stringify({
        detail: "Error al obtener usuario",
        error: error?.message || "Error desconocido",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    )
  }
}
