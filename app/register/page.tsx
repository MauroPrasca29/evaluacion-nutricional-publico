"use client"
import { useRouter } from "next/navigation"
import { useEffect } from "react"

export default function RegisterPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirigir inmediatamente al login
    router.push("/login")
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-6xl mb-4">🔒</div>
          <h1 className="text-2xl font-semibold mb-2">Registro No Disponible</h1>
          <p className="text-gray-600 mb-6">
            Por razones de seguridad, solo los administradores pueden crear nuevas cuentas de usuario.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Si necesitas acceso al sistema, contacta con el administrador.
          </p>
          <button
            onClick={() => router.push("/login")}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Ir al inicio de sesión
          </button>
        </div>
      </div>
    </div>
  )
}
