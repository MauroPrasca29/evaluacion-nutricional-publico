"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const router = useRouter()
  const [correo, setCorreo] = useState("")
  const [contrasena, setContrasena] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    try {
      // Send request to local auth endpoint (simplified endpoint, no proxy layer)
      const loginUrl = `/api/auth-login`
      console.log('Login: using endpoint ->', loginUrl)

      const res = await fetch(loginUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          correo: correo,
          contrasena: contrasena,
        }),
      })

      if (!res.ok) {
        // Intentar parsear JSON, si no, usar text
        let detail = ''
        try {
          const data = await res.json()
          detail = data.detail || data.message || JSON.stringify(data)
        } catch (e) {
          try {
            detail = await res.text()
          } catch (_) {
            detail = ''
          }
        }
        const statusMsg = `${res.status}${res.statusText ? ' ' + res.statusText : ''}`
        const userMsg = detail ? `${statusMsg}: ${detail}` : `${statusMsg}: Credenciales inválidas o error en el servidor`
        setError(userMsg)
        console.error('Login failed:', statusMsg, detail)
        setLoading(false)
        return
      }

      const data = await res.json()
      // Guardar token y redirigir
      localStorage.setItem("token", data.access_token)
      router.push("/")
    } catch (err) {
      setError("Error de conexión")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-semibold mb-4">Iniciar sesión</h1>
        {error && <div className="text-sm text-red-600 mb-3 p-2 bg-red-50 rounded">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Correo</label>
            <input
              type="email"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              required
              className="mt-1 block w-full border rounded p-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              value={contrasena}
              onChange={(e) => setContrasena(e.target.value)}
              required
              className="mt-1 block w-full border rounded p-2"
            />
          </div>

          <div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? "Accediendo..." : "Entrar"}
            </button>
          </div>
        </form>

        <div className="mt-4 text-center text-sm text-gray-600">
          ¿No tienes cuenta?{" "}
          <button
            onClick={() => router.push("/register")}
            className="text-blue-600 hover:underline font-medium"
          >
            Crear una aquí
          </button>
        </div>
      </div>
    </div>
  )
}
