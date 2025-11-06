# backend/src/api/reports.py
# Endpoints de reportes a partir de un import_id existente (cargado con /import/excel)

from __future__ import annotations

import io
import math
from datetime import date, datetime
from typing import Dict, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse, StreamingResponse

# Reutilizamos el almacenamiento del import
from src.api.import_excel import VectorStore

router = APIRouter(prefix="/reports", tags=["Reports"])


# ----------------- Utilidades -----------------
def _to_str(v) -> str:
    return "" if v is None or (isinstance(v, float) and math.isnan(v)) else str(v).strip()

def _parse_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        s = str(v).replace(",", ".").strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None

def _parse_date(v) -> Optional[date]:
    if v is None:
        return None
    if isinstance(v, date):
        return v
    s = str(v).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    try:
        return pd.to_datetime(v).date()
    except Exception:
        return None

def _age_years(born: Optional[date]) -> Optional[float]:
    if not born:
        return None
    today = date.today()
    try:
        years = (today - born).days / 365.25
        return round(years, 2)
    except Exception:
        return None

def _bmi(weight_kg: Optional[float], height_cm: Optional[float]) -> Optional[float]:
    if not weight_kg or not height_cm:
        return None
    try:
        h = height_cm / 100.0
        if h <= 0:
            return None
        return round(weight_kg / (h * h), 2)
    except Exception:
        return None

def _bmi_category(bmi: Optional[float]) -> str:
    if bmi is None:
        return "unknown"
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obesity"

def _load_dataframe(import_id: str) -> pd.DataFrame:
    store = VectorStore(import_id)
    if not store.load():
        raise HTTPException(status_code=404, detail="No existe vector store para ese import_id")
    df = pd.DataFrame(store.payloads).copy()

    expected = [
        "document_type", "document_number", "first_name", "last_name",
        "sex", "birth_date", "height_cm", "weight_kg", "notes"
    ]
    for c in expected:
        if c not in df.columns:
            df[c] = np.nan

    df["sex"] = df["sex"].apply(lambda x: _to_str(x).upper())
    df["birth_date_parsed"] = df["birth_date"].apply(_parse_date)
    df["age_years"] = df["birth_date_parsed"].apply(_age_years)

    df["height_cm_num"] = df["height_cm"].apply(_parse_float)
    df["weight_kg_num"] = df["weight_kg"].apply(_parse_float)
    df["bmi"] = df.apply(lambda r: _bmi(r["weight_kg_num"], r["height_cm_num"]), axis=1)
    df["bmi_category"] = df["bmi"].apply(_bmi_category)

    return df


# ----------------- Endpoints -----------------
@router.get("/", summary="Listado de endpoints de reportes")
async def reports_index():
    return {
        "endpoints": [
            "GET /api/reports/import/{import_id}/summary",
            "GET /api/reports/import/{import_id}/export",
        ]
    }


@router.get(
    "/import/{import_id}/summary",
    summary="Resumen del dataset importado (conteos, promedios, BMI)"
)
async def import_summary(
    import_id: str = Path(..., description="ID devuelto por /import/excel")
) -> JSONResponse:
    df = _load_dataframe(import_id)

    total_rows = int(len(df))
    sex_counts = df["sex"].value_counts(dropna=False).to_dict()

    age_mean = float(np.nanmean(df["age_years"])) if df["age_years"].notna().any() else None
    height_mean = float(np.nanmean(df["height_cm_num"])) if df["height_cm_num"].notna().any() else None
    weight_mean = float(np.nanmean(df["weight_kg_num"])) if df["weight_kg_num"].notna().any() else None
    bmi_mean = float(np.nanmean(df["bmi"])) if df["bmi"].notna().any() else None

    bmi_categories = df["bmi_category"].value_counts(dropna=False).to_dict()

    preview_cols = [
        "document_type", "document_number", "first_name", "last_name",
        "sex", "birth_date", "height_cm", "weight_kg", "bmi", "bmi_category"
    ]
    preview_cols = [c for c in preview_cols if c in df.columns or c in ["bmi", "bmi_category"]]
    preview = df[preview_cols].head(10).fillna("").to_dict(orient="records")

    return JSONResponse(
        content={
            "import_id": import_id,
            "total_rows": total_rows,
            "sex_counts": sex_counts,
            "means": {
                "age_years": age_mean,
                "height_cm": height_mean,
                "weight_kg": weight_mean,
                "bmi": bmi_mean,
            },
            "bmi_categories": bmi_categories,
            "preview_first_10": preview,
        }
    )


@router.get(
    "/import/{import_id}/export",
    summary="Exportar Excel con cálculos (edad, BMI)"
)
async def export_enriched_excel(
    import_id: str = Path(..., description="ID devuelto por /import/excel")
):
    df = _load_dataframe(import_id)

    out_cols = [
        "document_type", "document_number", "first_name", "last_name",
        "sex", "birth_date", "height_cm", "weight_kg",
        "age_years", "bmi", "bmi_category", "notes"
    ]
    for c in out_cols:
        if c not in df.columns:
            df[c] = ""

    export_df = df[out_cols].copy()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="reporte")
    output.seek(0)

    filename = f"reporte_{import_id}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename=\"{filename}\"'}
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
