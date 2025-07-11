"use client"

import { useState } from "react"
import { Bell, X, AlertTriangle, Info, CheckCircle, Clock } from "lucide-react"
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
}

interface NotificationPanelProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationPanel({ isOpen, onClose }: NotificationPanelProps) {
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: 1,
      type: "alert",
      title: "Alerta Nutricional",
      message: "María González presenta signos de desnutrición moderada. Requiere seguimiento inmediato.",
      time: "Hace 2 horas",
      read: false,
      childName: "María González",
    },
    {
      id: 2,
      type: "warning",
      title: "Seguimiento Pendiente",
      message: "Carlos Rodríguez tiene una cita de seguimiento programada para mañana.",
      time: "Hace 4 horas",
      read: false,
      childName: "Carlos Rodríguez",
    },
    {
      id: 3,
      type: "info",
      title: "Nuevo Registro",
      message: "Se ha registrado un nuevo niño en el sistema: Ana López.",
      time: "Hace 1 día",
      read: true,
      childName: "Ana López",
    },
    {
      id: 4,
      type: "success",
      title: "Evaluación Completada",
      message: "Se completó exitosamente la evaluación nutricional de Pedro Martínez.",
      time: "Hace 2 días",
      read: true,
      childName: "Pedro Martínez",
    },
    {
      id: 5,
      type: "alert",
      title: "Riesgo de Anemia",
      message: "Sofía Ramírez presenta síntomas compatibles con anemia. Revisar exámenes.",
      time: "Hace 3 días",
      read: false,
      childName: "Sofía Ramírez",
    },
  ])

  const markAsRead = (id: number) => {
    setNotifications((prev) => prev.map((notif) => (notif.id === id ? { ...notif, read: true } : notif)))
  }

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((notif) => ({ ...notif, read: true })))
  }

  const deleteNotification = (id: number) => {
    setNotifications((prev) => prev.filter((notif) => notif.id !== id))
  }

  const getIcon = (type: string) => {
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

  const getBadgeColor = (type: string) => {
    switch (type) {
      case "alert":
        return "bg-red-100 text-red-800"
      case "warning":
        return "bg-orange-100 text-orange-800"
      case "info":
        return "bg-blue-100 text-blue-800"
      case "success":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
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
            <div className="space-y-1">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                    !notification.read ? "bg-blue-50/50" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1">
                      {getIcon(notification.type)}
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
                          <span className="text-xs text-slate-500">{notification.time}</span>
                          {notification.childName && (
                            <Badge variant="outline" className="text-xs">
                              {notification.childName}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col gap-1">
                      {!notification.read && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => markAsRead(notification.id)}
                          className="h-6 px-2 text-xs"
                        >
                          Marcar leída
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteNotification(notification.id)}
                        className="h-6 px-2 text-xs text-red-600 hover:text-red-700"
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {notifications.length === 0 && (
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
