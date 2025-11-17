// Helper para llamadas a la API que añade Authorization automáticamente
export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  // Obtener token en runtime del cliente
  let token: string | null = null
  if (typeof window !== "undefined") {
    try {
      token = localStorage.getItem("token")
    } catch (e) {
      // ignore
    }
  }

  const headers = new Headers(init?.headers || {})
  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json")
  }

  const merged: RequestInit = { ...(init || {}), headers }
  return fetch(input, merged)
}

export async function apiJson(input: RequestInfo | URL, init?: RequestInit) {
  const res = await apiFetch(input, init)
  const text = await res.text()
  let data: any = null
  try {
    data = text ? JSON.parse(text) : null
  } catch (e) {
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

export function getApiBase(): string {
  const envBase = (process.env.NEXT_PUBLIC_API_BASE as string) || ""
  if (typeof window === "undefined") {
    return envBase || "http://localhost:8000"
  }

  // If running in a Codespaces / preview environment, prefer mapping from -3000 -> -8000
  try {
    const host = window.location.hostname
    if (host.includes("-3000") || host.endsWith(".github.dev")) {
      // Map preview frontend host to preview backend host
      if (host.includes("-3000")) {
        return `${window.location.protocol}//${host.replace("-3000", "-8000")}`
      }
    }
  } catch (e) {
    // ignore
  }

  // Otherwise, use envBase if provided
  if (envBase) {
    return envBase
  }

  // Fallbacks for local dev
  if (typeof window !== "undefined") {
    if (window.location.port === "3000") return `${window.location.protocol}//${window.location.hostname}:8000`
    return `${window.location.protocol}//${window.location.hostname}`
  }
  return "http://localhost:8000"
}
