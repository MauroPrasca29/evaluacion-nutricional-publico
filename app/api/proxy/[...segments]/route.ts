import { NextResponse } from 'next/server'

const BACKEND_BASE = process.env.BACKEND_BASE || process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

function copyAllowedResponseHeaders(source: Headers) {
  const dest: Record<string, string> = {}
  source.forEach((value, key) => {
    // skip hop-by-hop headers
    const skip = ['transfer-encoding', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'upgrade']
    if (skip.includes(key.toLowerCase())) return
    dest[key] = value
  })
  return dest
}

export async function GET(request: Request, { params }: { params: { segments: string[] } }) {
  return proxyRequest(request, params)
}

export async function POST(request: Request, { params }: { params: { segments: string[] } }) {
  return proxyRequest(request, params)
}

export async function PUT(request: Request, { params }: { params: { segments: string[] } }) {
  return proxyRequest(request, params)
}

export async function DELETE(request: Request, { params }: { params: { segments: string[] } }) {
  return proxyRequest(request, params)
}

export async function OPTIONS(request: Request, { params }: { params: { segments: string[] } }) {
  // Let CORS preflight be handled here by returning allowed methods/headers
  const headers = new Headers()
  headers.set('Access-Control-Allow-Origin', request.headers.get('origin') || '*')
  headers.set('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
  headers.set('Access-Control-Allow-Headers', request.headers.get('access-control-request-headers') || '*')
  headers.set('Access-Control-Allow-Credentials', 'true')
  return new Response(null, { status: 204, headers })
}

async function proxyRequest(request: Request, params: { segments: string[] }) {
  try {
    const segments = params.segments || []
    const path = segments.join('/')
    const targetUrl = `${BACKEND_BASE}/${path}`

    // Forward headers (but override host)
    const forwardHeaders: Record<string, string> = {}
    request.headers.forEach((v, k) => {
      // skip host header
      if (k.toLowerCase() === 'host') return
      forwardHeaders[k] = v
    })

    const body = await request.arrayBuffer()

    const resp = await fetch(targetUrl, {
      method: request.method,
      headers: forwardHeaders,
      body: body.byteLength > 0 ? body : undefined,
      // allow internal cookies if backend uses them
      credentials: 'include',
    })

    const respBody = await resp.arrayBuffer()
    const headers = copyAllowedResponseHeaders(resp.headers)
    // Ensure CORS headers are present when responding to the browser
    headers['Access-Control-Allow-Origin'] = request.headers.get('origin') || '*'
    headers['Access-Control-Allow-Credentials'] = 'true'

    return new Response(respBody, { status: resp.status, headers })
  } catch (err: any) {
    console.error('Proxy error:', err)
    return new Response(JSON.stringify({ detail: 'Proxy error', error: String(err) }), { status: 502, headers: { 'Content-Type': 'application/json' } })
  }
}
