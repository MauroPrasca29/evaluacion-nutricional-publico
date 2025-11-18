"use client"

import { useState, useEffect } from "react"
import { User, Shield, Bell, Save, Camera, Mail, Phone, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"

interface UserProfileProps {
  isOpen: boolean
  onClose: () => void
  userData?: {
    id_usuario: number
    nombre: string
    correo: string
    telefono: string
  } | null
}

export function UserProfile({ isOpen, onClose, userData }: UserProfileProps) {
  const [profileData, setProfileData] = useState({
    name: userData?.nombre || "Cargando...",
    email: userData?.correo || "",
    phone: userData?.telefono || "",
    position: "Nutricionista",
    institution: "Centro de Salud",
    license: "NUT-2019-001234",
    address: "Dirección no especificada",
    bio: "Profesional de la salud dedicado al seguimiento nutricional infantil.",
  })

  // Actualizar profileData cuando userData cambie
  useEffect(() => {
    if (!userData) return
    const raf = requestAnimationFrame(() => {
      setProfileData(prev => ({
        ...prev,
        name: userData.nombre,
        email: userData.correo,
        phone: userData.telefono,
      }))
    })
    return () => cancelAnimationFrame(raf)
  }, [userData])

  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    pushNotifications: true,
    weeklyReports: true,
    criticalAlerts: true,
  })

  const [security, setSecurity] = useState({
    twoFactor: false,
    sessionTimeout: "30",
    passwordExpiry: "90",
  })

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  const [passwordError, setPasswordError] = useState("")

  const handleChangePassword = async () => {
    setPasswordError("")

    // Validaciones
    if (!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword) {
      setPasswordError("Todos los campos son requeridos")
      return
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError("Las contraseñas nuevas no coinciden")
      return
    }

    if (passwordData.newPassword.length < 8) {
      setPasswordError("La nueva contraseña debe tener al menos 8 caracteres")
      return
    }

    try {
      const token = localStorage.getItem("token")
      if (!token) return

      const response = await fetch("/api/auth-change-password", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword,
        }),
      })

      if (response.ok) {
        alert("Contraseña actualizada exitosamente")
        setPasswordData({ currentPassword: "", newPassword: "", confirmPassword: "" })
      } else {
        const error = await response.json()
        setPasswordError(error.detail || "No se pudo cambiar la contraseña")
      }
    } catch (error) {
      console.error("Error changing password:", error)
      setPasswordError("Error al cambiar la contraseña")
    }
  }

  const handleSave = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) return

      // Actualizar perfil
      const response = await fetch("/api/auth-update-profile", {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nombre: profileData.name,
          telefono: profileData.phone,
        }),
      })

      if (response.ok) {
        alert("Perfil actualizado exitosamente")
        onClose()
        // Recargar la página para reflejar cambios
        window.location.reload()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail || "No se pudo actualizar el perfil"}`)
      }
    } catch (error) {
      console.error("Error saving profile:", error)
      alert("Error al guardar los cambios")
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-4xl bg-white shadow-xl border-0 max-h-[90vh] overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
          <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <User className="w-5 h-5" />
            Perfil de Usuario
          </CardTitle>
          <Button variant="ghost" onClick={onClose}>
            ✕
          </Button>
        </CardHeader>

        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          <Tabs defaultValue="profile" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mx-6 mt-4">
              <TabsTrigger value="profile" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                Perfil
              </TabsTrigger>
              <TabsTrigger value="notifications" className="flex items-center gap-2">
                <Bell className="w-4 h-4" />
                Notificaciones
              </TabsTrigger>
              <TabsTrigger value="security" className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Seguridad
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="p-6 space-y-6">
              {/* Información básica */}
              <Card className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Información Personal</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Avatar y datos básicos */}
                  <div className="flex items-center gap-6">
                    <div className="relative">
                      <Avatar className="w-24 h-24">
                        <AvatarImage src="/placeholder.svg" alt="Foto de perfil" />
                        <AvatarFallback className="bg-gradient-to-br from-amber-400 to-amber-500 text-white text-xl font-bold">
                          {userData ? userData.nombre.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2) : "NN"}
                        </AvatarFallback>
                      </Avatar>
                      <Button
                        size="sm"
                        className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0 bg-amber-500 hover:bg-amber-600"
                      >
                        <Camera className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-xl font-bold text-slate-800">{profileData.name}</h3>
                      <Badge className="bg-green-100 text-green-800">{profileData.position}</Badge>
                      <p className="text-sm text-slate-600">{profileData.institution}</p>
                    </div>
                  </div>

                  {/* Formulario de datos */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="name">Nombre Completo</Label>
                      <Input
                        id="name"
                        value={profileData.name}
                        onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                        className="border-amber-200 focus:border-amber-400"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Correo Electrónico</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <Input
                          id="email"
                          type="email"
                          value={profileData.email}
                          onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                          className="pl-10 border-amber-200 focus:border-amber-400"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">Teléfono</Label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <Input
                          id="phone"
                          value={profileData.phone}
                          onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                          className="pl-10 border-amber-200 focus:border-amber-400"
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="license">Número de Licencia</Label>
                      <Input
                        id="license"
                        value={profileData.license}
                        onChange={(e) => setProfileData({ ...profileData, license: e.target.value })}
                        className="border-amber-200 focus:border-amber-400"
                      />
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="address">Dirección</Label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                        <Input
                          id="address"
                          value={profileData.address}
                          onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                          className="pl-10 border-amber-200 focus:border-amber-400"
                        />
                      </div>
                    </div>
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="bio">Biografía Profesional</Label>
                      <Textarea
                        id="bio"
                        value={profileData.bio}
                        onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                        className="min-h-[100px] border-amber-200 focus:border-amber-400"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Estadísticas del usuario */}
              <Card className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Estadísticas de Actividad</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">156</div>
                      <div className="text-sm text-blue-700">Niños Evaluados</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">89</div>
                      <div className="text-sm text-green-700">Seguimientos</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">23</div>
                      <div className="text-sm text-orange-700">Alertas Resueltas</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">12</div>
                      <div className="text-sm text-purple-700">Reportes Generados</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="notifications" className="p-6 space-y-6">
              <Card className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Preferencias de Notificación</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-base font-medium">Alertas por Email</Label>
                      <p className="text-sm text-slate-600">Recibir notificaciones importantes por correo</p>
                    </div>
                    <Switch
                      checked={notifications.emailAlerts}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, emailAlerts: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-base font-medium">Notificaciones Push</Label>
                      <p className="text-sm text-slate-600">Notificaciones en tiempo real en el navegador</p>
                    </div>
                    <Switch
                      checked={notifications.pushNotifications}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, pushNotifications: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-base font-medium">Reportes Semanales</Label>
                      <p className="text-sm text-slate-600">Resumen semanal de actividades</p>
                    </div>
                    <Switch
                      checked={notifications.weeklyReports}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, weeklyReports: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-base font-medium">Alertas Críticas</Label>
                      <p className="text-sm text-slate-600">Notificaciones de casos urgentes</p>
                    </div>
                    <Switch
                      checked={notifications.criticalAlerts}
                      onCheckedChange={(checked) => setNotifications({ ...notifications, criticalAlerts: checked })}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="security" className="p-6 space-y-6">
              <Card className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Cambiar Contraseña</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {passwordError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                      {passwordError}
                    </div>
                  )}
                  <div className="space-y-2">
                    <Label htmlFor="currentPassword">Contraseña Actual</Label>
                    <Input
                      id="currentPassword"
                      type="password"
                      value={passwordData.currentPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="newPassword">Nueva Contraseña</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                    <p className="text-xs text-slate-500">Mínimo 8 caracteres</p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirmar Nueva Contraseña</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <Button
                    onClick={handleChangePassword}
                    className="w-full bg-gradient-to-r from-amber-400 to-amber-500 text-white"
                  >
                    Cambiar Contraseña
                  </Button>
                </CardContent>
              </Card>

              <Card className="border border-slate-200">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-slate-800">Configuración de Seguridad</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-base font-medium">Autenticación de Dos Factores</Label>
                      <p className="text-sm text-slate-600">Agregar una capa extra de seguridad (Próximamente)</p>
                    </div>
                    <Switch
                      checked={security.twoFactor}
                      onCheckedChange={(checked) => setSecurity({ ...security, twoFactor: checked })}
                      disabled
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sessionTimeout">Tiempo de Sesión (minutos)</Label>
                    <Input
                      id="sessionTimeout"
                      type="number"
                      value={security.sessionTimeout}
                      onChange={(e) => setSecurity({ ...security, sessionTimeout: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                      disabled
                    />
                    <p className="text-xs text-slate-500">Configuración próximamente</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end gap-4 p-6 border-t">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button onClick={handleSave} className="bg-gradient-to-r from-amber-400 to-amber-500 text-white">
              <Save className="w-4 h-4 mr-2" />
              Guardar Cambios
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
