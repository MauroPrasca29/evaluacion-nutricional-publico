// lib/api.ts

// ===========================================================
//    Obtener la URL base del backend FastAPI
// ===========================================================

export function getApiBase(): string {
  // 1) URL definida como variable pública (Vercel)
  const envBase = process.env.NEXT_PUBLIC_API_BASE

  if (envBase && envBase.trim().length > 0) {
    return envBase
  }

  // 2) Si estamos en el navegador durante desarrollo local
  if (typeof window !== "undefined") {
    const protocol = window.location.protocol
    return `${protocol}//localhost:8000`
  }

  // 3) SSR / fallback seguro
  return "http://localhost:8000"
}

// ===========================================================
//    Request con token automático (Bearer from localStorage)
// ===========================================================

export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  let token: string | null = null

  // Token solo existe en el cliente
  if (typeof window !== "undefined") {
    try {
      token = localStorage.getItem("token")
    } catch {
      // Ignorar errores de localStorage
    }
  }

  const headers = new Headers(init?.headers || {})

  // Inyectar Bearer token si existe
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json")
  }

  const mergedInit: RequestInit = {
    ...(init || {}),
    headers,
  }

  return fetch(input, mergedInit)
}

// ===========================================================
//    JSON Helper con manejo de errores automático
// ===========================================================

export async function apiJson(
  input: RequestInfo | URL,
  init?: RequestInit
) {
  const res = await apiFetch(input, init)
  const text = await res.text()

  let data: any = null
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }

  if (!res.ok) {
    const err: any = new Error("API Error")
    err.status = res.status
    err.data = data
    throw err
  }

  return data
}
