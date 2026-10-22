"""Script de prueba para verificar la función de configuración."""

import sys
import os

# Añadir el directorio actual al path para importar módulos locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ultramsg import get_user_config_path
from ui.main_window import get_user_config_path as ui_get_user_config_path

def test_config_paths():
    """Prueba las rutas de configuración."""
    print("=== PRUEBA DE RUTAS DE CONFIGURACIÓN ===")
    
    # Probar función desde ultramsg.py
    config_path_1 = get_user_config_path()
    print(f"Ruta desde ultramsg.py: {config_path_1}")
    
    # Probar función desde main_window.py  
    config_path_2 = ui_get_user_config_path()
    print(f"Ruta desde main_window.py: {config_path_2}")
    
    # Verificar que ambas dan la misma ruta
    if config_path_1 == config_path_2:
        print("✅ Ambas funciones devuelven la misma ruta")
    else:
        print("❌ ERROR: Las funciones devuelven rutas diferentes")
        
    # Verificar que el directorio se puede crear
    try:
        os.makedirs(os.path.dirname(config_path_1), exist_ok=True)
        print("✅ Directorio de configuración creado correctamente")
    except Exception as e:
        print(f"❌ ERROR creando directorio: {e}")
        
    # Verificar permisos de escritura
    try:
        test_file = config_path_1 + ".test"
        with open(test_file, 'w') as f:
            f.write('{"test": true}')
        os.remove(test_file)
        print("✅ Permisos de escritura verificados")
    except Exception as e:
        print(f"❌ ERROR de permisos de escritura: {e}")
        
    print(f"\n🎯 RUTA FINAL DE CONFIGURACIÓN:")
    print(f"   {config_path_1}")

if __name__ == "__main__":
    test_config_paths()
