"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function RegisterPage() {
  const router = useRouter()
  const [nombre, setNombre] = useState("")
  const [correo, setCorreo] = useState("")
  const [telefono, setTelefono] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    try {
      const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || 'http://127.0.0.1:8100'
      const apiBase = (process.env.NEXT_PUBLIC_API_URL as string) || 'http://localhost:8100'
      const res = await fetch(`${apiBase}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, correo, telefono, contrasena }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail || "Error al registrar")
        setLoading(false)
        return
      }

      // Registro exitoso: mostrar mensaje y redirigir al login
      const successMsg = document.createElement("div")
      successMsg.className = "fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow"
      successMsg.textContent = "¡Cuenta creada! Redirigiendo..."
      document.body.appendChild(successMsg)
      setTimeout(() => {
        router.push("/login")
      }, 1500)
    } catch (err) {
      setError("Error de conexión")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-semibold mb-4">Crear cuenta</h1>
        {error && <div className="text-sm text-red-600 mb-3 p-2 bg-red-50 rounded">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nombre</label>
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required className="mt-1 block w-full border rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Correo</label>
            <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required className="mt-1 block w-full border rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Teléfono</label>
            <input value={telefono} onChange={(e) => setTelefono(e.target.value)} required className="mt-1 block w-full border rounded p-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required className="mt-1 block w-full border rounded p-2" />
          </div>
          <div>
            <button type="submit" disabled={loading} className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:bg-gray-400">{loading ? "Creando..." : "Crear cuenta"}</button>
          </div>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          ¿Ya tienes cuenta?{" "}
          <button
            onClick={() => router.push("/login")}
            className="text-blue-600 hover:underline font-medium"
          >
            Inicia sesión aquí
          </button>
        </div>
      </div>
    </div>
  )
}
