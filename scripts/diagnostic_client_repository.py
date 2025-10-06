#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la instanciación de ClientRepositoryFacade
después de resolver los problemas de herencia y métodos abstractos.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from planificador.database.database import db_manager
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade


async def test_client_repository_facade():
    """
    Prueba la instanciación de ClientRepositoryFacade y verifica que no tenga
    métodos abstractos pendientes.
    """
    print("🔍 Iniciando diagnóstico de ClientRepositoryFacade...")
    
    try:
        # Obtener sesión de base de datos
        print("📊 Obteniendo sesión de base de datos...")
        
        async with db_manager.get_session() as session:
            print("✅ Sesión de base de datos obtenida correctamente")
            
            # Intentar instanciar ClientRepositoryFacade
            print("🏗️  Intentando instanciar ClientRepositoryFacade...")
            facade = ClientRepositoryFacade(session)
            print("✅ ClientRepositoryFacade instanciado correctamente")
            
            # Verificar que no hay métodos abstractos
            print("🔍 Verificando métodos abstractos...")
            abstract_methods = getattr(facade.__class__, '__abstractmethods__', set())
            
            if abstract_methods:
                print(f"❌ ClientRepositoryFacade aún tiene métodos abstractos: {abstract_methods}")
                return False
            else:
                print("✅ ClientRepositoryFacade no tiene métodos abstractos pendientes")
            
            # Verificar que los módulos se inicializaron correctamente
            print("🔍 Verificando inicialización de módulos...")
            
            modules_to_check = [
                ('_crud_operations', 'CrudOperations'),
                ('_advanced_query_operations', 'AdvancedQueryOperations'),
                ('_validation_operations', 'ValidationOperations'),
                ('_relationship_operations', 'RelationshipOperations')
            ]
            
            for attr_name, module_name in modules_to_check:
                if hasattr(facade, attr_name):
                    module = getattr(facade, attr_name)
                    print(f"✅ {module_name} inicializado correctamente: {type(module).__name__}")
                    
                    # Verificar métodos abstractos en cada módulo
                    module_abstract_methods = getattr(module.__class__, '__abstractmethods__', set())
                    if module_abstract_methods:
                        print(f"❌ {module_name} tiene métodos abstractos: {module_abstract_methods}")
                        return False
                    else:
                        print(f"✅ {module_name} no tiene métodos abstractos pendientes")
                else:
                    print(f"❌ {module_name} no encontrado en facade")
                    return False
            
            print("\n🎉 ¡Diagnóstico completado exitosamente!")
            print("✅ ClientRepositoryFacade se puede instanciar correctamente")
            print("✅ Todos los módulos están inicializados")
            print("✅ No hay métodos abstractos pendientes")
            
            return True
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        print(f"📍 Tipo de error: {type(e).__name__}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        return False


def main():
    """Función principal del script de diagnóstico."""
    print("=" * 60)
    print("🔧 DIAGNÓSTICO DE CLIENT REPOSITORY FACADE")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_client_repository_facade())
        
        if result:
            print("\n" + "=" * 60)
            print("✅ DIAGNÓSTICO EXITOSO - ClientRepositoryFacade está listo")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ DIAGNÓSTICO FALLIDO - Revisar errores arriba")
            print("=" * 60)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error crítico en el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
