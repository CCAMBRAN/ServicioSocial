"""
Configuración de la conexión a MySQL usando SQLAlchemy (async)
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

# Configuración de la base de datos MySQL
MYSQL_USER = "root"
MYSQL_PASSWORD = ""  # En XAMPP por defecto no hay password
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "seguros_db_sql"

# URL de conexión async para MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Crear el engine async
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Mostrar SQL queries en consola (útil para desarrollo)
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_size=10,  # Número de conexiones en el pool
    max_overflow=20  # Conexiones adicionales permitidas
)

# Crear sessionmaker async
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base para los modelos SQLAlchemy
Base = declarative_base()


async def get_db_sql() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener una sesión de base de datos SQL
    
    Uso en FastAPI:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db_sql)):
            # usar db aquí
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db_sql():
    """
    Inicializar la base de datos SQL
    Crear todas las tablas definidas en los modelos
    """
    async with engine.begin() as conn:
        # Crear todas las tablas
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Base de datos MySQL inicializada correctamente")


async def close_db_sql():
    """
    Cerrar la conexión a la base de datos SQL
    """
    await engine.dispose()
    print("✅ Conexión a MySQL cerrada")


# Función para verificar la conexión
async def test_connection():
    """
    Probar la conexión a MySQL
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            print("✅ Conexión a MySQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return False
