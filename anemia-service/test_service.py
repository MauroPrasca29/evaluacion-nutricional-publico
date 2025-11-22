#!/usr/bin/env python3
"""
Script de prueba para el servicio de detección de anemia
Verifica que el modelo ONNX se carga correctamente y puede hacer predicciones
"""

import sys
import requests
import json
import time
from pathlib import Path

# Configuración
ANEMIA_SERVICE_URL = "http://localhost:8001"
TEST_IMAGE_PATH = "test_image.jpg"
TIMEOUT = 30

def print_header(text):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    """Imprime un mensaje de éxito"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime un mensaje de error"""
    print(f"❌ {text}")

def print_info(text):
    """Imprime un mensaje informativo"""
    print(f"ℹ️  {text}")

def check_health():
    """Verifica que el servicio esté saludable"""
    print_header("Verificando Salud del Servicio")
    
    try:
        print_info(f"Conectando a {ANEMIA_SERVICE_URL}/health...")
        response = requests.get(
            f"{ANEMIA_SERVICE_URL}/health",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Servicio saludable: {data}")
            return True
        else:
            print_error(f"Servicio retornó status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"No se puede conectar a {ANEMIA_SERVICE_URL}")
        print_info("¿El servicio está corriendo? Intenta: docker-compose up anemia-service")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def get_service_info():
    """Obtiene información del servicio"""
    print_header("Información del Servicio")
    
    try:
        response = requests.get(f"{ANEMIA_SERVICE_URL}/", timeout=TIMEOUT)
        data = response.json()
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print_error(f"No se pudo obtener información: {str(e)}")
        return False

def create_test_image():
    """Crea una imagen de prueba simple"""
    try:
        from PIL import Image
        import numpy as np
        
        # Crear imagen 256x256 aleatoria (simula una imagen de conjuntiva)
        img_array = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        img.save(TEST_IMAGE_PATH)
        print_success(f"Imagen de prueba creada: {TEST_IMAGE_PATH}")
        return True
    except ImportError:
        print_error("Pillow no instalado. Instala: pip install pillow numpy")
        return False
    except Exception as e:
        print_error(f"No se pudo crear imagen de prueba: {str(e)}")
        return False

def test_prediction(age_months=24):
    """Prueba una predicción"""
    print_header(f"Probando Predicción (Edad: {age_months} meses)")
    
    # Verificar que existe imagen de prueba
    if not Path(TEST_IMAGE_PATH).exists():
        print_info("No existe imagen de prueba. Creando...")
        if not create_test_image():
            return False
    
    try:
        print_info(f"Enviando imagen de prueba ({TEST_IMAGE_PATH})...")
        
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': f}
            data = {'age_months': age_months}
            
            response = requests.post(
                f"{ANEMIA_SERVICE_URL}/predict",
                files=files,
                data=data,
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Predicción exitosa!")
            print("\nResultado:")
            print(json.dumps(result, indent=2))
            
            # Validar estructura de respuesta
            required_fields = [
                "age_months",
                "hb_estimate_g_dL", 
                "threshold_g_dL",
                "anemia_flag",
                "anemia_label"
            ]
            
            missing_fields = [f for f in required_fields if f not in result]
            if missing_fields:
                print_error(f"Campos faltantes: {missing_fields}")
                return False
            
            print_success("✓ Estructura de respuesta correcta")
            return True
        else:
            print_error(f"Predicción fallida (status {response.status_code})")
            print_info(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Timeout: La predicción tardó demasiado")
        return False
    except Exception as e:
        print_error(f"Error en predicción: {str(e)}")
        return False

def test_multiple_ages():
    """Prueba predicciones con diferentes edades"""
    print_header("Probando Diferentes Grupos de Edad")
    
    test_cases = [
        (12, "6-59 meses (umbral: 12.0 g/dL)"),
        (36, "6-59 meses (umbral: 12.0 g/dL)"),
        (90, "60-131 meses (umbral: 12.25 g/dL)"),
        (120, "60-131 meses (umbral: 12.25 g/dL)"),
    ]
    
    results = []
    for age, description in test_cases:
        print_info(f"Probando: {description}")
        
        try:
            if not Path(TEST_IMAGE_PATH).exists():
                create_test_image()
            
            with open(TEST_IMAGE_PATH, 'rb') as f:
                files = {'file': f}
                data = {'age_months': age}
                
                response = requests.post(
                    f"{ANEMIA_SERVICE_URL}/predict",
                    files=files,
                    data=data,
                    timeout=TIMEOUT
                )
            
            if response.status_code == 200:
                result = response.json()
                status = "✅" if result['anemia_label'] else "❌"
                results.append((age, result['hb_estimate_g_dL'], result['threshold_g_dL'], result['anemia_label']))
                print(f"  {status} Edad {age}m: Hb={result['hb_estimate_g_dL']:.2f} g/dL, "
                      f"Umbral={result['threshold_g_dL']:.2f} → {result['anemia_label']}")
            else:
                print_error(f"Falló para edad {age}m")
        except Exception as e:
            print_error(f"Error para edad {age}m: {str(e)}")
    
    if results:
        print_success(f"✓ Se completaron {len(results)} pruebas")
        return True
    return False

def test_invalid_inputs():
    """Prueba con entradas inválidas"""
    print_header("Probando Validación de Entradas")
    
    tests = [
        {"age_months": -5, "name": "Edad negativa"},
        {"age_months": "invalid", "name": "Edad no numérica"},
    ]
    
    for test in tests:
        print_info(f"Probando: {test['name']}")
        
        try:
            if not Path(TEST_IMAGE_PATH).exists():
                create_test_image()
            
            with open(TEST_IMAGE_PATH, 'rb') as f:
                files = {'file': f}
                data = {'age_months': test['age_months']}
                
                response = requests.post(
                    f"{ANEMIA_SERVICE_URL}/predict",
                    files=files,
                    data=data,
                    timeout=TIMEOUT
                )
            
            if response.status_code != 200:
                print_success(f"✓ Validación correcta (status {response.status_code})")
            else:
                print_error(f"Debería haber fallado pero retornó 200")
        except Exception as e:
            print_info(f"Error capturado correctamente: {str(e)}")

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PRUEBAS DEL SERVICIO DE ANEMIA" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "health": check_health(),
        "info": get_service_info(),
        "prediction": test_prediction(),
        "multiple_ages": test_multiple_ages(),
        "invalid_inputs": test_invalid_inputs(),
    }
    
    print_header("Resumen de Resultados")
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print()
    if all_passed:
        print_success("¡Todas las pruebas pasaron!")
        print_info("El servicio de anemia está funcionando correctamente")
    else:
        print_error("Algunas pruebas fallaron")
        print_info("Revisa los logs: docker-compose logs anemia-service")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        sys.exit(1)
