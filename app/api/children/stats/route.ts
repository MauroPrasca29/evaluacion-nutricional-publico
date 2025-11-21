// app/api/children/stats/route.ts

const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    console.log(`🔄 [Children Stats] → ${BACKEND_BASE}/api/children/stats`)

    const response = await fetch(`${BACKEND_BASE}/api/children/stats`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // por si el backend usa auth más adelante
    })

    const text = await response.text()
    let data: any = {}

    try {
      data = text ? JSON.parse(text) : {}
    } catch (err) {
      console.error("❌ [Children Stats] Error parseando JSON:", err, text)
    }

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
  } catch (error: any) {
    console.error("❌ [Children Stats Error]:", error)
    return new Response(
      JSON.stringify({
        detail: "Error al obtener estadísticas de niños",
        error: error?.message ?? "Error desconocido",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    )
  }
}
