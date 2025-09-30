#!/usr/bin/env bash
set -euo pipefail

COMPOSE="infra/docker-compose.yml"

pass=(); fail=(); warn=()
step(){ echo -e "\n\033[1;34m▶ $*\033[0m"; }
ok(){   echo -e "  \033[32m✔ $*\033[0m"; pass+=("$*"); }
bad(){  echo -e "  \033[31m✘ $*\033[0m"; fail+=("$*"); }
note(){ echo -e "  \033[33m⚠ $*\033[0m"; warn+=("$*"); }

# Detecta el .env para docker compose (prioriza infra/.env)
ENVFLAGS=()
if [[ -f infra/.env ]]; then
  ENVFLAGS=(--env-file infra/.env)
elif [[ -f .env ]]; then
  ENVFLAGS=(--env-file .env)
fi

# ===== 1) Seguridad y configuración =====
step "1) Seguridad y configuración"
[[ -f .env.example ]] && ok ".env.example existe" || bad "Falta .env.example"

# Falsa alarma: solo marca si el valor NO empieza con '<'
if [[ -f .env.example ]] && grep -qiE 'postgres(ql)?(\+psycopg2)?://[^<]|^[[:space:]]*[A-Za-z_]*PASSWORD=[^<]|^[[:space:]]*SECRET_KEY=[^<]' .env.example; then
  bad ".env.example parece contener secretos reales"
fi

git check-ignore -q .env && ok ".env ignorado" || bad ".env no ignorado"
git check-ignore -q .dockerignore && bad ".dockerignore está ignorado" || ok ".dockerignore versionable"
if git check-ignore -q alembic/versions/0001_init.py 2>/dev/null; then
  bad "migraciones Alembic ignoradas"
else
  ok "migraciones Alembic versionables"
fi
[[ -f LICENSE ]] && ok "LICENSE" || note "Falta LICENSE"
[[ -f .editorconfig ]] && ok ".editorconfig" || note "Falta .editorconfig"
[[ -f README.md ]] && ok "README" || note "Falta README"

# ===== 2) Tooling unificado =====
step "2) Tooling unificado"
command -v pre-commit >/dev/null 2>&1 && ok "pre-commit instalado" || note "pre-commit no instalado"
[[ -f .pre-commit-config.yaml ]] && ok ".pre-commit-config.yaml" || note "Falta .pre-commit-config.yaml"
[[ -f backend/requirements.txt ]] && ok "backend/requirements.txt" || bad "Falta backend/requirements.txt"
{ [[ -f pnpm-lock.yaml ]] || [[ -f package-lock.json ]] || [[ -f yarn.lock ]]; } && ok "Lockfile FE" || note "Falta lockfile FE"
[[ -f Makefile ]] && ok "Makefile" || note "Falta Makefile"

# ===== 3) Infra Docker estable =====
step "3) Infra Docker estable"
# Intenta levantar (silencioso). No falla si algo no arranca.
docker compose "${ENVFLAGS[@]}" -f "$COMPOSE" up -d >/dev/null 2>&1 || true
sleep 2
if curl -fsS http://localhost/healthz >/dev/null 2>&1; then
  ok "Nginx /healthz OK"
else
  bad "Nginx /healthz FAIL"
fi
if curl -fsS http://localhost/api/healthz | grep -q '"status":"ok"'; then
  ok "Backend /api/healthz OK"
else
  bad "Backend /api/healthz FAIL"
fi

# ===== 4) Base de datos =====
step "4) Base de datos"
if docker compose -f "$COMPOSE" exec -T backend alembic current >/tmp/alembic_current 2>/dev/null; then
  if grep -qE '[0-9]{4,}_.+' /tmp/alembic_current; then
    ok "Alembic aplicado: $(tr -d '\r' </tmp/alembic_current)"
  else
    note "Alembic no aplicado"
  fi
else
  note "No se pudo consultar Alembic"
fi

# Usa variables DENTRO del contenedor db
if docker compose -f "$COMPOSE" exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT name FROM roles ORDER BY 1;"' >/tmp/roles 2>/dev/null; then
  if grep -q 'admin' /tmp/roles; then
    ok "Seeds roles OK"
  else
    note "Roles no detectados (ejecuta app.seed)"
  fi
else
  note "No se pudo consultar DB (psql)"
fi

# ===== 5) Auth básico =====
step "5) Auth básico"
EMAIL="$(docker compose -f "$COMPOSE" exec -T backend printenv ADMIN_EMAIL 2>/dev/null | tr -d '\r\n' || true)"
PASS="$(docker compose -f "$COMPOSE" exec -T backend printenv ADMIN_INITIAL_PASSWORD 2>/dev/null | tr -d '\r\n' || true)"
[[ -z "$EMAIL" ]] && EMAIL="${ADMIN_EMAIL:-admin@example.com}"
[[ -z "$PASS"  ]] && PASS="${ADMIN_INITIAL_PASSWORD:-changeme}"

ACCESS="$(curl -fsS -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' \
  -d "{\"username\":\"$EMAIL\",\"password\":\"$PASS\"}" 2>/dev/null | python - <<'PY' || true
import sys,json
try:
  d=json.load(sys.stdin); print(d.get("access",""))
except: print("")
PY
)"
if echo "$ACCESS" | grep -qE '^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'; then
  ok "Login devuelve JWT"
else
  note "Login no válido (revisar seed/credenciales)"
fi

# ===== 6) Frontend mínimo =====
step "6) Frontend"
if curl -fsSI http://localhost | head -n1 | grep -q ' 200 '; then
  ok "Frontend responde 200 en /"
else
  note "Frontend no responde 200 en /"
fi

# ===== 7) OpenAPI =====
step "7) OpenAPI"
if curl -fsS http://localhost/openapi.json >/dev/null 2>&1; then
  ok "openapi.json accesible"
else
  note "openapi.json no accesible"
fi
[[ -f docs/openapi.yaml ]] && ok "docs/openapi.yaml versionado" || note "Falta docs/openapi.yaml"

# ===== Resumen =====
step "Resumen"
echo "✔ OK: ${#pass[@]}  ⚠ WARN: ${#warn[@]}  ✘ FAIL: ${#fail[@]}"
((${#fail[@]}==0)) || exit 1
