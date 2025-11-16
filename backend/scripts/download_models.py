#!/usr/bin/env python3
"""
Script para descargar modelos ONNX desde Google Drive.

Uso:
    python download_models.py [--models-dir /path/to/models]

Variantes de ID de Google Drive (por si los archivos se mueven):
    - Pueden ser IDs de archivo directo (gdown) o URLs compartidas.
"""

import os
import sys
import argparse
import urllib.request
import shutil
from pathlib import Path

# Google Drive file IDs (reemplazar con los IDs correctos si es necesario)
MODELS = {
    "hb_regressor_infants_ft.onnx": "1QrGj4hNFmJ9rkXpK6xYzZ7mAaBbCcDdEe",  # Reemplazar con tu ID
    "hb_regressor_infants_ft.pth": "1FgHiJkLmNoPqRsT8uVwXyZ1AbCdEfGhIj",   # Reemplazar con tu ID
}

def download_from_drive(file_id: str, output_path: str, filename: str) -> bool:
    """
    Descargar archivo desde Google Drive usando gdown o requests.
    
    Args:
        file_id: ID del archivo en Google Drive
        output_path: Ruta donde guardar el archivo
        filename: Nombre del archivo
    
    Returns:
        True si la descarga fue exitosa, False en caso contrario
    """
    try:
        # Intentar usar gdown si está disponible
        try:
            import gdown
            url = f"https://drive.google.com/uc?id={file_id}"
            output_file = os.path.join(output_path, filename)
            print(f"📥 Descargando {filename} desde Google Drive...")
            gdown.download(url, output_file, quiet=False)
            if os.path.exists(output_file):
                print(f"✅ {filename} descargado correctamente.")
                return True
            else:
                print(f"❌ Error: {filename} no se guardó correctamente.")
                return False
        except ImportError:
            # Si gdown no está disponible, usar método alternativo
            print(f"⚠️  gdown no está disponible, intentando método alternativo...")
            
            # URL directa para descarga compartida (puede requerir ajuste según compartir settings)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            output_file = os.path.join(output_path, filename)
            
            print(f"📥 Descargando {filename}...")
            urllib.request.urlretrieve(url, output_file)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"✅ {filename} descargado correctamente.")
                return True
            else:
                print(f"❌ Error: {filename} no se guardó correctamente.")
                return False
                
    except Exception as e:
        print(f"❌ Error descargando {filename}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Descargar modelos ONNX desde Google Drive."
    )
    parser.add_argument(
        "--models-dir",
        default="/app/models",
        help="Directorio donde guardar los modelos (default: /app/models)"
    )
    
    args = parser.parse_args()
    models_dir = args.models_dir
    
    # Crear directorio si no existe
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"📁 Directorio de modelos: {models_dir}")
    
    all_success = True
    for filename, file_id in MODELS.items():
        filepath = os.path.join(models_dir, filename)
        
        # Verificar si el modelo ya existe
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✓ {filename} ya existe ({size_mb:.1f} MB).")
            continue
        
        # Descargar
        if not download_from_drive(file_id, models_dir, filename):
            all_success = False
            print(f"⚠️  No se pudo descargar {filename}")
    
    if all_success:
        print("\n✅ Todos los modelos están disponibles.")
        return 0
    else:
        print("\n⚠️  Algunos modelos no se descargaron correctamente. Verifica los IDs o la conectividad.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
