import sys
import os
from pathlib import Path

# Agregar la ruta del proyecto al path de Python
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.database import connect_to_mongo, close_mongo_connection
from app.database_sql import init_db_sql, close_db_sql
from app import models
import uvicorn

async def crear_seguros_economicos(app: FastAPI):
    """Crear paquetes de seguros económicos automáticamente si no existen"""
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.database import DATABASE_NAME, MONGODB_URL
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Verificar si ya existen seguros
    seguros_count = await db.seguros.count_documents({})
    if seguros_count == 0:
        seguros_economicos = [
            models.SeguroCreate(
                nombre="Seguro Básico Familiar",
                descripcion="Protección esencial para tu familia a un precio accesible",
                duracion_meses=12,
                precio=50.00,
                cuota_mensual=25.00,
                cobertura=10000.00,
                tipo="basico",
                beneficios="✓ Asistencia médica básica\n✓ Apoyo en gastos funerarios\n✓ Asistencia legal básica"
            ),
            models.SeguroCreate(
                nombre="Seguro Estándar Hogar",
                descripcion="Protección completa para tu hogar y familia",
                duracion_meses=12,
                precio=100.00,
                cuota_mensual=45.00,
                cobertura=25000.00,
                tipo="estandar",
                beneficios="✓ Cobertura médica amplia\n✓ Protección del hogar\n✓ Asistencia educativa\n✓ Apoyo por incapacidad"
            ),
            models.SeguroCreate(
                nombre="Seguro Premium Integral",
                descripcion="Protección máxima con los mejores beneficios",
                duracion_meses=12,
                precio=150.00,
                cuota_mensual=65.00,
                cobertura=50000.00,
                tipo="premium",
                beneficios="✓ Cobertura médica completa\n✓ Protección de ingresos\n✓ Asistencia educativa premium\n✓ Apoyo por desempleo\n✓ Asesoría financiera"
            )
        ]
        
        for seguro_data in seguros_economicos:
            seguro = models.Seguro(**seguro_data.model_dump())
            await db.seguros.insert_one(seguro.model_dump())
        
        print("✅ Paquetes de seguros económicos creados automáticamente")
    
    client.close()

app = FastAPI(
    title="Sistema de Seguros API",
    description="Backend para sistema de seguros de ahorro",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    # Conectar a MongoDB
    try:
        await connect_to_mongo()
        print("✅ Conectado a MongoDB")
    except Exception as e:
        print(f"⚠️  No se pudo conectar a MongoDB: {e}")
    
    # Inicializar MySQL (comentado - comentar si no necesitas MySQL)
    try:
        await init_db_sql()
        print("✅ Conectado a MySQL")
    except Exception as e:
        print(f"⚠️  No se pudo conectar a MySQL: {e}")
    
    # Crear seguros iniciales en MongoDB
    try:
        await crear_seguros_economicos(app)
    except Exception as e:
        print(f"⚠️  No se pudieron crear seguros iniciales: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    # Cerrar MongoDB
    try:
        await close_mongo_connection()
        print("✅ Desconectado de MongoDB")
    except Exception as e:
        print(f"⚠️  Error al cerrar MongoDB: {e}")
    
    # Cerrar MySQL (comentado - comentar si no necesitas MySQL)
    try:
        await close_db_sql()
        print("✅ Desconectado de MySQL")
    except Exception as e:
        print(f"⚠️  Error al cerrar MySQL: {e}")

# Incluir rutas de la API
app.include_router(router, prefix="/api/v1")

# Servir archivos estáticos del frontend (debe ir al final)
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)