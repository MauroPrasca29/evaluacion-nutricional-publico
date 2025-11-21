import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/children/alerts/count`, {
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      return NextResponse.json(
        { count: 0 },
        { status: 200 }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in alerts count route:', error)
    return NextResponse.json({ count: 0 }, { status: 200 })
  }
}