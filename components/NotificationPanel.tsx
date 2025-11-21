"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Bell, X, AlertTriangle, Info, CheckCircle, Clock, Upload, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Notification {
  id: number
  type: "alert" | "info" | "success" | "warning"
  title: string
  message: string
  time: string
  read: boolean
  childName?: string
  infanteId?: number
  seguimientoId?: number
  userName?: string
  tipoActividad?: string
}

interface NotificationPanelProps {
  isOpen: boolean
  onClose: () => void
  onAlertsUpdate?: () => void
}

export function NotificationPanel({ isOpen, onClose, onAlertsUpdate }: NotificationPanelProps) {
  const router = useRouter()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      fetchNotifications()
    }
  }, [isOpen])

  const fetchNotifications = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/children/alerts?limit=20')
      if (response.ok) {
        const data = await response.json()
        setNotifications(data)
      }
    } catch (error) {
      console.error('Error cargando notificaciones:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    if (notification.infanteId && notification.tipoActividad !== "importacion") {
      // Navegar al perfil del infante (solo si no es importación)
      router.push(`/children/${notification.infanteId}`)
      onClose()
    }
  }

  const markAsRead = (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setNotifications((prev) => prev.map((notif) => (notif.id === id ? { ...notif, read: true } : notif)))
  }

  const deleteNotification = (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setNotifications((prev) => prev.filter((notif) => notif.id !== id))
    if (onAlertsUpdate) {
      onAlertsUpdate()
    }
  }

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((notif) => ({ ...notif, read: true })))
    if (onAlertsUpdate) {
      onAlertsUpdate()
    }
  }

  const getIcon = (type: string, tipoActividad?: string) => {
    if (tipoActividad === "importacion") {
      return <Upload className="w-4 h-4 text-purple-500" />
    }
    if (tipoActividad === "seguimiento") {
      return <FileText className="w-4 h-4 text-blue-500" />
    }
    
    switch (type) {
      case "alert":
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case "warning":
        return <Clock className="w-4 h-4 text-orange-500" />
      case "info":
        return <Info className="w-4 h-4 text-blue-500" />
      case "success":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      default:
        return <Bell className="w-4 h-4 text-gray-500" />
    }
  }

  const unreadCount = notifications.filter((n) => !n.read).length

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-end p-4">
      <Card className="w-full max-w-md bg-white shadow-xl border-0 mt-16 mr-4">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notificaciones
            {unreadCount > 0 && <Badge className="bg-red-500 text-white text-xs px-2 py-1">{unreadCount}</Badge>}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="flex justify-between items-center px-6 pb-4">
            <Button variant="ghost" size="sm" onClick={markAllAsRead} disabled={unreadCount === 0}>
              Marcar todas como leídas
            </Button>
          </div>

          <ScrollArea className="h-96">
            {loading ? (
              <div className="p-8 text-center">
                <p className="text-slate-500">Cargando notificaciones...</p>
              </div>
            ) : (
              <div className="space-y-1">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                      notification.infanteId && notification.tipoActividad !== "importacion" ? 'cursor-pointer' : ''
                    } ${!notification.read ? "bg-blue-50/50" : ""}`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1">
                        {getIcon(notification.type, notification.tipoActividad)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h4
                              className={`text-sm font-medium text-slate-800 ${
                                !notification.read ? "font-semibold" : ""
                              }`}
                            >
                              {notification.title}
                            </h4>
                            {!notification.read && <div className="w-2 h-2 bg-blue-500 rounded-full"></div>}
                          </div>
                          <p className="text-sm text-slate-600 mb-2">{notification.message}</p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-400">{notification.time}</span>
                            <div className="flex items-center gap-2">
                              {/* Solo mostrar el nombre del usuario si NO es una alerta */}
                              {notification.userName && notification.tipoActividad !== "alerta" && (
                                <Badge variant="outline" className="text-xs">
                                  {notification.userName}
                                </Badge>
                              )}
                              {/* Mostrar el nombre del infante solo en alertas */}
                              {notification.childName && notification.tipoActividad === "alerta" && (
                                <Badge variant="outline" className="text-xs bg-red-50 text-red-700 border-red-200">
                                  {notification.childName}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col gap-1">
                        {!notification.read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => markAsRead(notification.id, e)}
                            className="h-6 px-2 text-xs"
                          >
                            Marcar leída
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => deleteNotification(notification.id, e)}
                          className="h-6 px-2 text-xs text-red-600 hover:text-red-700"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>

          {!loading && notifications.length === 0 && (
            <div className="p-8 text-center">
              <Bell className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">No hay notificaciones</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}