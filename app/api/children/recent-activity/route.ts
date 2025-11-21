const BACKEND_BASE = "https://backend-production-73f7.up.railway.app"

export async function GET() {
  try {
    console.log(
      `🔄 [Children Recent Activity] → ${BACKEND_BASE}/api/children/recent-activity`,
    )

    const response = await fetch(
      `${BACKEND_BASE}/api/children/recent-activity`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      },
    )

    const text = await response.text()
    let data: any = {}

    try {
      data = text ? JSON.parse(text) : {}
    } catch (err) {
      console.error(
        "❌ [Children Recent Activity] Error parseando JSON:",
        err,
        text,
      )
    }

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
  } catch (error: any) {
    console.error("❌ [Children Recent Activity Error]:", error)
    return new Response(
      JSON.stringify({
        detail: "Error al obtener actividad reciente",
        error: error?.message ?? "Error desconocido",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    )
  }
}
