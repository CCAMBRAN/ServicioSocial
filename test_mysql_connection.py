"""
Script para probar la conexión a MySQL y crear las tablas
"""
import asyncio
from app.database_sql import init_db_sql, test_connection, close_db_sql


async def main():
    print("=" * 60)
    print("PROBANDO CONEXIÓN A MYSQL")
    print("=" * 60)
    
    # 1. Probar conexión
    print("\n1. Verificando conexión a MySQL...")
    conexion_exitosa = await test_connection()
    
    if not conexion_exitosa:
        print("\n❌ No se pudo conectar a MySQL")
        print("Verifica que:")
        print("  - XAMPP esté ejecutando MySQL")
        print("  - La base de datos 'seguros_db_sql' exista")
        print("  - Usuario: root, Password: (vacío)")
        return
    
    # 2. Crear tablas
    print("\n2. Creando tablas en la base de datos...")
    try:
        await init_db_sql()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return
    
    # 3. Cerrar conexión
    print("\n3. Cerrando conexión...")
    await close_db_sql()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("\nAhora puedes:")
    print("  1. Abrir phpMyAdmin (http://localhost/phpmyadmin)")
    print("  2. Ver la base de datos 'seguros_db_sql'")
    print("  3. Verificar que se crearon las 5 tablas")
    print("     - usuarios")
    print("     - seguros")
    print("     - polizas")
    print("     - pagos")
    print("     - auditoria")


if __name__ == "__main__":
    asyncio.run(main())
