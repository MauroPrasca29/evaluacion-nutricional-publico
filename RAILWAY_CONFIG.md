# Configuración de Variables de Entorno en Railway

## ⚠️ IMPORTANTE: Variables Faltantes en Railway

Actualmente el frontend está intentando conectar al backend pero **NO sabe a dónde ir** porque falta la variable `BACKEND_BASE`.

## 🔧 Pasos para Configurar en Railway

### 1. **Para el servicio FRONTEND (Vercel)**

Si estás usando Vercel, ve a:
- **Vercel Dashboard** → Tu proyecto → **Settings** → **Environment Variables**

Agrega estas variables:

```
BACKEND_BASE=http://backend-production-73f7.up.railway.app
NEXT_PUBLIC_API_BASE=http://backend-production-73f7.up.railway.app
```

**Luego redeploy:**
- En Vercel → Deployments → Redeploy

### 2. **Si estás deployando TODO en Railway**

Ve a Railway:
- Tu proyecto → **Frontend service** → **Variables**

Agrega:

```
BACKEND_BASE=http://backend-production-73f7.up.railway.app
NEXT_PUBLIC_API_BASE=http://backend-production-73f7.up.railway.app
NODE_ENV=production
```

### 3. **Verificar URL del Backend**

La URL que necesitas es:
```
http://backend-production-73f7.up.railway.app
```

O si tienes un dominio personalizado:
```
https://tu-dominio.com/backend
```

## 🔍 Cómo Verificar que Funciona

1. Abre DevTools (F12) en el navegador
2. Ve a **Console** y **Network**
3. Intenta hacer login
4. Ve qué URL se está llamando (debería ser `http://backend-production-73f7.up.railway.app/api/auth/login`)

## 📋 Variables Locales (docker-compose)

Para desarrollo local, ya están configuradas en `.env`:
```
BACKEND_BASE=http://backend:8000
NEXT_PUBLIC_API_BASE=http://backend:8000
```

## ✅ Checklist de Configuración

- [ ] Variable `BACKEND_BASE` configurada en Vercel/Railway
- [ ] Variable `NEXT_PUBLIC_API_BASE` configurada en Vercel/Railway
- [ ] Frontend redesplegado después de cambios
- [ ] Prueba de login funciona correctamente
- [ ] Checks en DevTools muestran status 200/201 en requests

---

**Problema:** Sin `BACKEND_BASE`, el frontend no sabe a dónde enviar las peticiones → Error 500

**Solución:** Configurar la variable en Railway/Vercel → Frontend sabrá la URL exacta del backend

