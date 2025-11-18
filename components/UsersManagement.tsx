"use client"

import { useState, useEffect } from "react"
import { Users, Search, UserPlus, Edit, Trash2, Shield, Key } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { ThemeColors } from "@/types"

interface User {
  id_usuario: number
  nombre: string
  correo: string
  telefono: string
  rol_id: number | null
  fecha_creado: string
  fecha_actualizado: string
}

interface Role {
  id_rol: number
  nombre: string
  descripcion: string | null
}

interface UsersManagementProps {
  theme: ThemeColors
}

export function UsersManagement({ theme }: UsersManagementProps) {
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [resetPasswordModal, setResetPasswordModal] = useState(false)
  const [editUserModal, setEditUserModal] = useState(false)
  const [deleteUserModal, setDeleteUserModal] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [resetting, setResetting] = useState(false)
  const [updating, setUpdating] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [createUserModal, setCreateUserModal] = useState(false)
  const [editUserData, setEditUserData] = useState({
    nombre: "",
    telefono: "",
    rol_id: null as number | null
  })
  const [newUserData, setNewUserData] = useState({
    nombre: "",
    correo: "",
    telefono: "",
    contrasena: "",
    confirmContrasena: ""
  })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchUsers()
    fetchRoles()
  }, [])

  useEffect(() => {
    // Filtrar usuarios por nombre o correo
    const filtered = users.filter(user =>
      user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.correo.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredUsers(filtered)
  }, [searchTerm, users])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) return

      const response = await fetch("/api/users", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data)
        setFilteredUsers(data)
      } else {
        console.error("Error fetching users")
      }
    } catch (error) {
      console.error("Error:", error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoles = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) return

      const response = await fetch("/api/roles", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setRoles(data)
      } else {
        console.error("Error fetching roles")
      }
    } catch (error) {
      console.error("Error:", error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric"
    })
  }

  const handleResetPassword = (user: User) => {
    setSelectedUser(user)
    setNewPassword("")
    setConfirmPassword("")
    setResetPasswordModal(true)
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setEditUserData({
      nombre: user.nombre,
      telefono: user.telefono,
      rol_id: user.rol_id
    })
    setEditUserModal(true)
  }

  const handleDeleteUser = (user: User) => {
    setSelectedUser(user)
    setDeleteUserModal(true)
  }

  const deleteUser = async () => {
    if (!selectedUser) return

    setDeleting(true)
    try {
      const token = localStorage.getItem("token")
      if (!token) return

      const response = await fetch(`/api/users/${selectedUser.id_usuario}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })

      if (response.ok) {
        const result = await response.json()
        alert(`✅ ${result.message}`)
        setDeleteUserModal(false)
        setSelectedUser(null)
        // Recargar lista de usuarios
        fetchUsers()
      } else {
        const error = await response.json()
        alert(`❌ Error: ${error.detail || "No se pudo eliminar el usuario"}`)
      }
    } catch (error) {
      console.error("Error al eliminar usuario:", error)
      alert(`❌ Error de conexión: ${error instanceof Error ? error.message : "No se pudo eliminar el usuario"}`)
    } finally {
      setDeleting(false)
    }
  }

  const updateUser = async () => {
    if (!selectedUser) return

    // Validaciones
    if (!editUserData.nombre || !editUserData.telefono) {
      alert("El nombre y teléfono son obligatorios")
      return
    }

    setUpdating(true)
    try {
      const token = localStorage.getItem("token")
      if (!token) return

      console.log("🔍 Actualizando usuario:", {
        userId: selectedUser.id_usuario,
        userName: selectedUser.nombre,
        userEmail: selectedUser.correo,
        newData: editUserData
      })

      const response = await fetch(`/api/users/${selectedUser.id_usuario}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(editUserData)
      })

      if (response.ok) {
        const updatedUser = await response.json()
        alert(`✅ Usuario ${updatedUser.nombre} actualizado exitosamente`)
        setEditUserModal(false)
        setSelectedUser(null)
        // Recargar lista de usuarios
        fetchUsers()
      } else {
        const error = await response.json()
        alert(`❌ Error: ${error.detail || "No se pudo actualizar el usuario"}`)
      }
    } catch (error) {
      console.error("Error al actualizar usuario:", error)
      alert(`❌ Error de conexión: ${error instanceof Error ? error.message : "No se pudo actualizar el usuario"}`)
    } finally {
      setUpdating(false)
    }
  }

  const resetPassword = async () => {
    if (!selectedUser) return

    // Validaciones
    if (!newPassword || newPassword.length < 8) {
      alert("La contraseña debe tener al menos 8 caracteres")
      return
    }

    if (newPassword !== confirmPassword) {
      alert("Las contraseñas no coinciden")
      return
    }

    setResetting(true)
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        alert("❌ Sesión expirada. Por favor, inicie sesión nuevamente.")
        return
      }

      const response = await fetch(`/api/users/${selectedUser.id_usuario}/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ new_password: newPassword })
      })

      if (response.ok) {
        const data = await response.json()
        alert(`✅ ${data.message}`)
        setResetPasswordModal(false)
        setNewPassword("")
        setConfirmPassword("")
        setSelectedUser(null)
      } else {
        const error = await response.json()
        alert(`❌ Error: ${error.detail || "No se pudo restablecer la contraseña"}`)
      }
    } catch (error) {
      console.error("Error al restablecer contraseña:", error)
      alert(`❌ Error de conexión: ${error instanceof Error ? error.message : "No se pudo restablecer la contraseña"}`)
    } finally {
      setResetting(false)
    }
  }

  const handleCreateUser = () => {
    setNewUserData({
      nombre: "",
      correo: "",
      telefono: "",
      contrasena: "",
      confirmContrasena: ""
    })
    setCreateUserModal(true)
  }

  const createUser = async () => {
    // Validaciones
    if (!newUserData.nombre || !newUserData.correo || !newUserData.telefono || !newUserData.contrasena) {
      alert("Todos los campos son obligatorios")
      return
    }

    if (newUserData.contrasena.length < 8) {
      alert("La contraseña debe tener al menos 8 caracteres")
      return
    }

    if (newUserData.contrasena !== newUserData.confirmContrasena) {
      alert("Las contraseñas no coinciden")
      return
    }

    setCreating(true)
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        alert("❌ Sesión expirada. Por favor, inicie sesión nuevamente.")
        return
      }

      const response = await fetch("/api/auth-register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: newUserData.nombre,
          correo: newUserData.correo,
          telefono: newUserData.telefono,
          contrasena: newUserData.contrasena
        })
      })

      if (response.ok) {
        alert(`✅ Usuario ${newUserData.nombre} creado exitosamente`)
        setCreateUserModal(false)
        setNewUserData({
          nombre: "",
          correo: "",
          telefono: "",
          contrasena: "",
          confirmContrasena: ""
        })
        // Recargar lista de usuarios
        fetchUsers()
      } else {
        const error = await response.json()
        alert(`❌ Error: ${error.detail || "No se pudo crear el usuario"}`)
      }
    } catch (error) {
      console.error("Error al crear usuario:", error)
      alert(`❌ Error de conexión: ${error instanceof Error ? error.message : "No se pudo crear el usuario"}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-600" />
            Gestión de Usuarios
          </h1>
          <p className="text-slate-600 mt-1">Administra los usuarios del sistema</p>
        </div>
        <Button 
          onClick={handleCreateUser}
          className="bg-gradient-to-r from-blue-500 to-blue-600 text-white"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Nuevo Usuario
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <Input
                placeholder="Buscar por nombre o correo..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">
            Usuarios del Sistema ({filteredUsers.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-slate-500">Cargando usuarios...</div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              {searchTerm ? "No se encontraron usuarios" : "No hay usuarios registrados"}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3 font-semibold text-slate-700">ID</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Nombre</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Correo</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Teléfono</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Rol</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Fecha Registro</th>
                    <th className="text-left p-3 font-semibold text-slate-700">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user) => (
                    <tr key={user.id_usuario} className="border-b hover:bg-slate-50">
                      <td className="p-3 text-slate-600">{user.id_usuario}</td>
                      <td className="p-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-sm">
                            {user.nombre.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                          </div>
                          <span className="font-medium text-slate-800">{user.nombre}</span>
                        </div>
                      </td>
                      <td className="p-3 text-slate-600">{user.correo}</td>
                      <td className="p-3 text-slate-600">{user.telefono}</td>
                      <td className="p-3">
                        {user.rol_id ? (
                          <Badge variant="outline">
                            <Shield className="w-3 h-3 mr-1" />
                            {roles.find(r => r.id_rol === user.rol_id)?.nombre || `Rol ${user.rol_id}`}
                          </Badge>
                        ) : (
                          <Badge variant="secondary">Sin rol</Badge>
                        )}
                      </td>
                      <td className="p-3 text-slate-600 text-sm">
                        {formatDate(user.fecha_creado)}
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="hover:bg-blue-50 hover:text-blue-600"
                            onClick={() => handleEditUser(user)}
                            title="Editar usuario"
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="hover:bg-orange-50 hover:text-orange-600"
                            onClick={() => handleResetPassword(user)}
                            title="Restablecer contraseña"
                          >
                            <Key className="w-4 h-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="hover:bg-red-50 hover:text-red-600"
                            onClick={() => handleDeleteUser(user)}
                            title="Eliminar usuario"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{users.length}</div>
              <div className="text-sm text-slate-600 mt-1">Total Usuarios</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {users.filter(u => u.rol_id).length}
              </div>
              <div className="text-sm text-slate-600 mt-1">Con Rol Asignado</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {users.filter(u => !u.rol_id).length}
              </div>
              <div className="text-sm text-slate-600 mt-1">Sin Rol</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {users.filter(u => {
                  const createdDate = new Date(u.fecha_creado)
                  const lastWeek = new Date()
                  lastWeek.setDate(lastWeek.getDate() - 7)
                  return createdDate >= lastWeek
                }).length}
              </div>
              <div className="text-sm text-slate-600 mt-1">Última Semana</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Edit User Modal */}
      <Dialog open={editUserModal} onOpenChange={setEditUserModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Usuario</DialogTitle>
            <DialogDescription>
              Modificar datos de <strong>{selectedUser?.nombre}</strong> ({selectedUser?.correo})
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="editNombre">Nombre Completo</Label>
              <Input
                id="editNombre"
                value={editUserData.nombre}
                onChange={(e) => setEditUserData({...editUserData, nombre: e.target.value})}
                placeholder="Ej: Juan Pérez"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="editTelefono">Teléfono</Label>
              <Input
                id="editTelefono"
                value={editUserData.telefono}
                onChange={(e) => setEditUserData({...editUserData, telefono: e.target.value})}
                placeholder="3001234567"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="editRol">Rol</Label>
              <Select
                value={editUserData.rol_id?.toString() || "0"}
                onValueChange={(value) => setEditUserData({...editUserData, rol_id: value === "0" ? null : parseInt(value)})}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Sin rol</SelectItem>
                  {roles.map((rol) => (
                    <SelectItem key={rol.id_rol} value={rol.id_rol.toString()}>
                      {rol.nombre}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {editUserData.rol_id && (
                <p className="text-sm text-slate-500">
                  {roles.find(r => r.id_rol === editUserData.rol_id)?.descripcion}
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setEditUserModal(false)
                setSelectedUser(null)
              }}
              disabled={updating}
            >
              Cancelar
            </Button>
            <Button
              onClick={updateUser}
              disabled={updating || !editUserData.nombre || !editUserData.telefono}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {updating ? "Actualizando..." : "Actualizar Usuario"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create User Modal */}
      <Dialog open={createUserModal} onOpenChange={setCreateUserModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Crear Nuevo Usuario</DialogTitle>
            <DialogDescription>
              Completa los datos del nuevo usuario del sistema
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="createNombre">Nombre Completo</Label>
              <Input
                id="createNombre"
                value={newUserData.nombre}
                onChange={(e) => setNewUserData({...newUserData, nombre: e.target.value})}
                placeholder="Ej: Juan Pérez"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="createCorreo">Correo Electrónico</Label>
              <Input
                id="createCorreo"
                type="email"
                value={newUserData.correo}
                onChange={(e) => setNewUserData({...newUserData, correo: e.target.value})}
                placeholder="usuario@ejemplo.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="createTelefono">Teléfono</Label>
              <Input
                id="createTelefono"
                value={newUserData.telefono}
                onChange={(e) => setNewUserData({...newUserData, telefono: e.target.value})}
                placeholder="3001234567"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="createPassword">Contraseña</Label>
              <Input
                id="createPassword"
                type="password"
                value={newUserData.contrasena}
                onChange={(e) => setNewUserData({...newUserData, contrasena: e.target.value})}
                placeholder="Mínimo 8 caracteres"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="createConfirmPassword">Confirmar Contraseña</Label>
              <Input
                id="createConfirmPassword"
                type="password"
                value={newUserData.confirmContrasena}
                onChange={(e) => setNewUserData({...newUserData, confirmContrasena: e.target.value})}
                placeholder="Repita la contraseña"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setCreateUserModal(false)
                setNewUserData({
                  nombre: "",
                  correo: "",
                  telefono: "",
                  contrasena: "",
                  confirmContrasena: ""
                })
              }}
              disabled={creating}
            >
              Cancelar
            </Button>
            <Button
              onClick={createUser}
              disabled={creating || !newUserData.nombre || !newUserData.correo || !newUserData.telefono || !newUserData.contrasena}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {creating ? "Creando..." : "Crear Usuario"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reset Password Modal */}
      <Dialog open={resetPasswordModal} onOpenChange={setResetPasswordModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Restablecer Contraseña</DialogTitle>
            <DialogDescription>
              Establecer nueva contraseña para <strong>{selectedUser?.nombre}</strong> ({selectedUser?.correo})
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="newPassword">Nueva Contraseña</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Mínimo 8 caracteres"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmar Contraseña</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repita la contraseña"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setResetPasswordModal(false)
                setNewPassword("")
                setConfirmPassword("")
              }}
              disabled={resetting}
            >
              Cancelar
            </Button>
            <Button
              onClick={resetPassword}
              disabled={resetting || !newPassword || !confirmPassword}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {resetting ? "Restableciendo..." : "Restablecer"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete User Modal */}
      <Dialog open={deleteUserModal} onOpenChange={setDeleteUserModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-red-600">⚠️ Confirmar Eliminación</DialogTitle>
            <DialogDescription>
              ¿Está seguro que desea eliminar al usuario <strong>{selectedUser?.nombre}</strong> ({selectedUser?.correo})?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">
                <strong>⚠️ Advertencia:</strong> Esta acción no se puede deshacer. 
                Todos los datos asociados a este usuario permanecerán en el sistema pero sin un usuario asignado.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteUserModal(false)
                setSelectedUser(null)
              }}
              disabled={deleting}
            >
              Cancelar
            </Button>
            <Button
              onClick={deleteUser}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {deleting ? "Eliminando..." : "Sí, Eliminar Usuario"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
