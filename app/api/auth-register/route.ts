const BACKEND_BASE = process.env.BACKEND_BASE || 'http://localhost:8000'

export async function POST(request: Request) {
  try {
    const body = await request.json()

    const response = await fetch(`${BACKEND_BASE}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    const data = await response.json()

    return new Response(JSON.stringify(data), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    })
  } catch (error: any) {
    console.error('[Auth Register Error]', error)
    return new Response(
      JSON.stringify({ detail: 'Error en registro', error: error.message }),
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
