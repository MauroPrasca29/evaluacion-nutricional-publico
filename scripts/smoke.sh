#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8000}"

say() { printf "\n===> %s\n" "$*"; }

jq_test() { command -v jq >/dev/null 2>&1 || { echo "jq no está instalado"; exit 1; }; }
jq_test

say "BASE: $BASE"

say "Health"
curl -sS "$BASE/health" | jq
curl -sS "$BASE/healthz" | jq

say "Auth: register"
REGISTER_PAYLOAD='{"nombre":"Admin Local","correo":"admin@example.com","telefono":"3000000000","contrasena":"12345678"}'
curl -sS -X POST "$BASE/api/auth/register" -H "Content-Type: application/json" -d "$REGISTER_PAYLOAD" | jq || true

say "Auth: login (JSON)"
TOKEN="$(curl -sS -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" \
  -d '{"correo":"admin@example.com","contrasena":"12345678"}' | jq -r '.access_token')"
echo "TOKEN=${TOKEN:0:20}..."

say "Auth: me"
curl -sS "$BASE/api/auth/me" -H "Authorization: Bearer $TOKEN" | jq

say "Auth: token (OAuth2)"
curl -sS -X POST "$BASE/api/auth/token" -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=admin%40example.com&password=12345678' | jq

say "Children: ping"
curl -sS "$BASE/api/children/ping" | jq

say "Children: create"
CHILD_ID="$(curl -sS -X POST "$BASE/api/children/" -H "Content-Type: application/json" \
  -d '{"nombre":"Ana María Pérez Rojas","fecha_nacimiento":"2021-05-10","genero":"F","sede_id":1}' | jq -r '.id')"
echo "CHILD_ID=$CHILD_ID"

say "Children: list"
curl -sS "$BASE/api/children/?limit=10&offset=0" | jq

say "Children: get by id"
curl -sS "$BASE/api/children/$CHILD_ID" | jq

say "Children: update"
curl -sS -X PUT "$BASE/api/children/$CHILD_ID" -H "Content-Type: application/json" \
  -d '{"nombre":"Ana María P. Rojas","genero":"F"}' | jq

say "Followups: ping"
curl -sS "$BASE/api/followups/ping" | jq

say "Followups: create"
FOLLOWUP_ID="$(curl -sS -X POST "$BASE/api/followups/" -H "Content-Type: application/json" \
  -d "{\"child_id\": $CHILD_ID, \"fecha\": \"2025-10-23\", \"observacion\": \"Control mensual\"}" | jq -r '.id')"
echo "FOLLOWUP_ID=$FOLLOWUP_ID"

say "Followups: list"
curl -sS "$BASE/api/followups/?limit=10&offset=0" | jq

say "Followups: get by id"
curl -sS "$BASE/api/followups/$FOLLOWUP_ID" | jq

say "Followups: add symptom (codigo)"
SYM_ID="$(curl -sS -X POST "$BASE/api/followups/$FOLLOWUP_ID/symptoms" -H "Content-Type: application/json" \
  -d '{"codigo":"diarrea"}' | jq -r '.id_symptom // .id')"
echo "SYM_ID=$SYM_ID"

say "Followups: get symptom by id"
curl -sS "$BASE/api/followups/symptoms/$SYM_ID" | jq

say "Followups: update"
curl -sS -X PUT "$BASE/api/followups/$FOLLOWUP_ID" -H "Content-Type: application/json" \
  -d '{"observaciones":"Control mensual actualizado","peso_kg":14.2,"talla_cm":95.0}' | jq

say "Reports: ping"
curl -sS "$BASE/api/reports/ping" | jq

say "Reports: statistics"
curl -sS "$BASE/api/reports/statistics" | jq

say "Reports: export (stub)"
curl -sS -X POST "$BASE/api/reports/export" | jq || true

say "Reports: pdf by child (stub)"
curl -sS "$BASE/api/reports/pdf/$CHILD_ID" | jq

say "Import: ping"
curl -sS "$BASE/api/import/ping" | jq

say "Import: template"
curl -sS "$BASE/api/import/template" | jq

say "Import: upload excel"
TMPX="/tmp/fake.xlsx"
printf "" > "$TMPX"
curl -sS -X POST "$BASE/api/import/excel" -F "file=@$TMPX" | jq

say "Import: status"
curl -sS "$BASE/api/import/status/123" | jq

say "Followups: delete"
curl -sS -i -X DELETE "$BASE/api/followups/$FOLLOWUP_ID" | sed -n '1,5p'

say "Followups: get after delete (expect 404)"
curl -sS "$BASE/api/followups/$FOLLOWUP_ID" | jq || true

say "Children: delete"
curl -sS -i -X DELETE "$BASE/api/children/$CHILD_ID" | sed -n '1,5p'

say "Children: get after delete (expect 404)"
curl -sS "$BASE/api/children/$CHILD_ID" | jq || true

echo "✅ Pruebas completas."
