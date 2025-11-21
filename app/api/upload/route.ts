// app/api/import/upload/route.ts
import { NextRequest, NextResponse } from "next/server"

// 👇 Usamos primero BACKEND_BASE (server-only), luego NEXT_PUBLIC_API_URL, y como último recurso localhost.
const BACKEND_BASE =
  process.env.BACKEND_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000"

// ⚡ Configuración para permitir requests largos
export const maxDuration = 300 // 10 minutos (solo en Vercel Pro/Enterprise)
export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  try {
    console.log("📥 Proxy: Recibiendo request de importación")
    
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (file) {
      const fileSizeMB = file.size / (1024 * 1024)
      console.log(`📊 Proxy: Archivo recibido - ${file.name} (${fileSizeMB.toFixed(2)} MB)`)
    }
    
    console.log(`🔄 Proxy: Enviando a backend ${BACKEND_BASE}/api/import/upload`)
    const startTime = Date.now()
    
    // ⚡ Aumentar timeout a 10 minutos (600,000 ms)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      console.log("⏰ Proxy: Timeout de 10 minutos alcanzado")
      controller.abort()
    }, 600000)
    
    const response = await fetch(`${BACKEND_BASE}/api/import/upload`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
      // ⚡ Headers para debugging
      headers: {
        'X-Proxy-Start-Time': startTime.toString(),
      }
    })

    clearTimeout(timeoutId)
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(2)
    console.log(`✅ Proxy: Respuesta recibida del backend en ${elapsed}s`)

    // ⚡ Verificar content-type antes de parsear
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text()
      console.error(`❌ Proxy: Respuesta no-JSON del backend. Content-Type: ${contentType}`)
      console.error(`Respuesta: ${text.substring(0, 500)}...`)
      return NextResponse.json(
        { 
          success: false,
          detail: "El backend no respondió con JSON. Verifica los logs del servidor." 
        },
        { status: 500 }
      )
    }

    let data
    try {
      const text = await response.text()
      if (!text || text.trim().length === 0) {
        console.error("❌ Proxy: Respuesta vacía del backend")
        return NextResponse.json(
          { 
            success: false,
            detail: "El backend respondió con datos vacíos" 
          },
          { status: 500 }
        )
      }
      data = JSON.parse(text)
    } catch (parseError) {
      console.error("❌ Proxy: Error al parsear JSON del backend:", parseError)
      return NextResponse.json(
        { 
          success: false,
          detail: "Error al procesar la respuesta del backend" 
        },
        { status: 500 }
      )
    }

    if (!response.ok) {
      console.log(`⚠️ Proxy: Backend respondió con error ${response.status}`)
      return NextResponse.json(data, { status: response.status })
    }

    console.log(`🎉 Proxy: Importación exitosa - ${data.processed_count || 0} registros procesados`)
    return NextResponse.json(data)
    
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error("⏰ Proxy: Request abortado por timeout")
        return NextResponse.json(
          { 
            success: false,
            detail: "La importación tardó más de 10 minutos. Intenta con un archivo más pequeño." 
          },
          { status: 504 }
        )
      }
      console.error("❌ Proxy error:", error.message)
      console.error(error.stack)
    } else {
      console.error("❌ Proxy error desconocido:", error)
    }
    
    return NextResponse.json(
      { 
        success: false,
        detail: error instanceof Error ? error.message : "Error del servidor" 
      },
      { status: 500 }
    )
  }
}
