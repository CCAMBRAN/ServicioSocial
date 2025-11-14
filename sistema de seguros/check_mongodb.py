#!/usr/bin/env python3
"""
Script para verificar la conexión a MongoDB y el estado de la base de datos
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "seguros_db"

async def check_mongodb_connection():
    """Verifica la conexión a MongoDB y muestra el estado de la BD"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONEXIÓN A MONGODB")
    print("=" * 60)
    print(f"\n📍 URL de conexión: {MONGODB_URL}")
    
    try:
        # Intentar conectar
        print("\n⏳ Conectando a MongoDB...")
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Hacer ping
        await client.admin.command("ping")
        print("✅ Conexión exitosa a MongoDB")
        
        # Información de la base de datos
        db = client[DATABASE_NAME]
        print(f"\n📦 Base de datos: {DATABASE_NAME}")
        
        # Listar colecciones
        colecciones = await db.list_collection_names()
        if colecciones:
            print(f"📊 Colecciones encontradas ({len(colecciones)}):")
            for coleccion in colecciones:
                count = await db[coleccion].count_documents({})
                print(f"   • {coleccion}: {count} documentos")
        else:
            print("📊 No hay colecciones en la base de datos (vacía)")
        
        # Información detallada de cada colección
        if "seguros" in colecciones:
            print("\n📄 Muestreo de seguros:")
            siguros = await db.seguros.find({}).limit(2).to_list(2)
            for seg in siguros:
                print(f"   - {seg.get('nombre', 'Sin nombre')} (${seg.get('precio', 0)})")
        
        if "usuarios" in colecciones:
            print("\n👥 Muestreo de usuarios:")
            usuarios = await db.usuarios.find({}).limit(2).to_list(2)
            for usr in usuarios:
                print(f"   - {usr.get('nombre', 'Sin nombre')} ({usr.get('email', 'Sin email')})")
        
        client.close()
        print("\n" + "=" * 60)
        print("✅ ESTADO: La base de datos está conectada y disponible")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {type(e).__name__}: {e}")
        print("\n⚠️  ACCIONES A TOMAR:")
        print("   1. Verifica que MongoDB esté instalado")
        print("   2. Inicia el servicio MongoDB:")
        print("      - En Windows: services.msc y busca 'MongoDB Server'")
        print("      - En Windows (si instalaste con Chocolatey): brew services start mongodb-community")
        print("      - En Linux: sudo systemctl start mongod")
        print("   3. O inicia MongoDB manualmente en otra terminal:")
        print("      mongod")
        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    resultado = asyncio.run(check_mongodb_connection())
    sys.exit(0 if resultado else 1)
