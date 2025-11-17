# 🔐 Login y Registro - Implementación

## ✅ Estado

- ✓ Login funcional
- ✓ Register funcional
- ✓ Ambos endpoints disponibles en producción y preview
- ✓ Tokens se guardan en localStorage
- ✓ Redirección automática al dashboard

## 📝 Endpoints

### Login
```
POST /api/auth-login

Body:
{
  "correo": "usuario@example.com",
  "contrasena": "contraseña"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Register
```
POST /api/auth-register

Body:
{
  "nombre": "Nombre del usuario",
  "correo": "usuario@example.com",
  "telefono": "3001234567",
  "contrasena": "contraseña"
}

Response (201):
{
  "id_usuario": 1,
  "nombre": "Nombre del usuario",
  "correo": "usuario@example.com",
  "telefono": "3001234567",
  "fecha_creado": "2025-11-17T02:04:39.667709Z"
}
```

## 🏗️ Arquitectura

```
Navegador (Preview público)
    ↓
Next.js Frontend (puerto 3000)
    ↓
Endpoints Next.js (/api/auth-login, /api/auth-register)
    ↓
Backend FastAPI (puerto 8000, localhost)
    ↓
Base de datos PostgreSQL
```

## 🔧 Configuración

### Endpoints en Next.js
- `app/api/auth-login/route.ts` - Reenvía a `/api/auth/login` del backend
- `app/api/auth-register/route.ts` - Reenvía a `/api/auth/register` del backend

Ambos:
- Leen el `BACKEND_BASE` de variables de entorno (default: `http://localhost:8000`)
- Reenvían las peticiones al backend
- Devuelven el response con headers CORS apropiados

### Frontend
- `app/login/page.tsx` - Formulario de login, llamada a `/api/auth-login`
- `app/register/page.tsx` - Formulario de register, llamada a `/api/auth-register`
- `lib/api.ts` - Helper de fetch con Authorization header (para rutas protegidas)

### Backend
- `backend/src/api/auth.py`:
  - `POST /api/auth/register` - Crea nuevo usuario
  - `POST /api/auth/login` - Login con JSON (correo + contrasena)
  - `POST /api/auth/token` - Login con OAuth2 form-data
  - `GET /api/auth/me` - Perfil del usuario autenticado

## 🧪 Pruebas

### Localmente
```bash
# Login
curl -X POST http://localhost:3000/api/auth-login \
  -H "Content-Type: application/json" \
  -d '{"correo":"prueba@example.com","contrasena":"Prueba123!"}'

# Register
curl -X POST http://localhost:3000/api/auth-register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Usuario","correo":"nuevo@example.com","telefono":"3001234567","contrasena":"Pass123!"}'
```

### En navegador (preview público)
1. Abre `https://<tu-preview>.app.github.dev/login`
2. Ingresa credenciales (ejemplo: `prueba@example.com` / `Prueba123!`)
3. Haz clic en "Entrar"
4. Deberías ser redirigido a `/` (dashboard)

## 📦 Variables de Entorno

```env
# Backend (para que Next pueda alcanzarlo)
BACKEND_BASE=http://localhost:8000

# Frontend (para el navegador, si es necesario)
NEXT_PUBLIC_API_BASE=<url-pública-backend>  # Opcional
```

## 🚀 Para producción

1. Asegurar que `BACKEND_BASE` apunte a la URL correcta del backend en producción
2. Verificar que los headers CORS sean apropiados
3. Considerar usar cookies HttpOnly en lugar de localStorage para tokens
4. Implementar refresh tokens si es necesario

## 📝 Notas técnicas

- El token se guarda en `localStorage` bajo la clave `token`
- El cliente automáticamente incluye el token en el header `Authorization: Bearer <token>` (ver `lib/api.ts`)
- Los endpoints devuelven errores en formato JSON
- CORS está configurado para aceptar requests desde cualquier origen (considerar restringir en producción)

## ✨ Cambios futuros (opcionales)

- [ ] Usar cookies HttpOnly para tokens (más seguro)
- [ ] Implementar refresh tokens
- [ ] Agregar validación de contraseña más fuerte
- [ ] Implementar 2FA
- [ ] Rate limiting en endpoints de auth
- [ ] Logs de auditoría para login/register
