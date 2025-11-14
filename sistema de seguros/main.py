from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.database import connect_to_mongo, close_mongo_connection
from app import models
import uvicorn
import os

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
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos del frontend
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await crear_seguros_economicos(app)

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Sistema de Seguros API",
        "version": "3.0.0",
        "descripcion": "Sistema diseñado para hacer los seguros accesibles a todos"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)