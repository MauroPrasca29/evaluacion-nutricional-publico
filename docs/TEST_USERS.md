# Usuarios de Prueba

## Usuario por defecto

- **Email:** `prueba@example.com`
- **Contraseña:** `Prueba123!`
- **ID:** 7

## Crear un usuario nuevo

```bash
curl -X POST http://localhost:3000/api/auth-register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Tu Nombre",
    "correo": "tu@email.com",
    "telefono": "3001234567",
    "contrasena": "TuContraseña123!"
  }'
```

## Obtener token

```bash
curl -X POST http://localhost:3000/api/auth-login \
  -H "Content-Type: application/json" \
  -d '{"correo":"prueba@example.com","contrasena":"Prueba123!"}'
```

## Usando el token

```bash
curl http://localhost:3000/api/me \
  -H "Authorization: Bearer <TOKEN_AQUI>"
```
