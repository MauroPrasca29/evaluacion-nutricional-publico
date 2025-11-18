import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  const { userId } = await params
  try {
    const authHeader = request.headers.get("authorization")
    if (!authHeader) {
      return NextResponse.json({ detail: "No autorizado" }, { status: 401 })
    }

    const body = await request.json()

    const response = await fetch(
      `${BACKEND_BASE}/api/auth/users/${userId}/reset-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: authHeader,
        },
        body: JSON.stringify(body),
      }
    )

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error resetting password:", error)
    return NextResponse.json(
      { detail: "Error al restablecer la contraseña" },
      { status: 500 }
    )
  }
}
