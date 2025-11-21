// lib/api.ts

export function getApiBase(): string {
  const envBase = process.env.NEXT_PUBLIC_API_BASE

  if (envBase && envBase.trim().length > 0) {
    return envBase
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//localhost:8000`
  }

  return "http://localhost:8000"
}

export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  let token: string | null = null

  if (typeof window !== "undefined") {
    try {
      token = localStorage.getItem("token")
    } catch {}
  }

  const headers = new Headers(init?.headers || {})

  if (token) headers.set("Authorization", `Bearer ${token}`)
  if (!headers.has("Accept")) headers.set("Accept", "application/json")

  return fetch(input, { ...(init || {}), headers })
}

export async function apiJson(input: RequestInfo | URL, init?: RequestInit) {
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
