# 🔄 Sistema Híbrido: MongoDB + MySQL

## Arquitectura de Bases de Datos

Tu sistema ahora usa **DOS bases de datos** simultáneamente, cada una optimizada para diferentes tipos de datos.

---

## 📊 Distribución de Datos

### MongoDB (No Relacional)
**Base de datos**: `seguros_db`  
**Uso**: Catálogo de productos y datos flexibles

| Colección | Descripción | ¿Por qué MongoDB? |
|-----------|-------------|-------------------|
| **seguros** | Catálogo de productos de seguros | Estructura flexible, beneficios variables, fácil agregar campos |

**Ejemplo de datos**:
```json
{
  "id": "abc-123",
  "nombre": "Seguro Básico Familiar",
  "tipo": "basico",
  "precio": 50.00,
  "beneficios": "✓ Médico\n✓ Funeral\n✓ Legal",
  "activo": true
}
```

---

### MySQL (Relacional)
**Base de datos**: `seguros_db_sql`  
**Uso**: Datos transaccionales con integridad referencial

| Tabla | Descripción | ¿Por qué MySQL? |
|-------|-------------|-----------------|
| **usuarios** | Información de clientes | Requiere integridad, constraints únicos (email) |
| **polizas** | Contratos usuario-seguro | Relación FK estricta, validaciones |
| **pagos** | Historial de transacciones | Integridad transaccional, auditoría |
| **auditoria** | Log de cambios | Registro cronológico estructurado |

**Relaciones**:
```
usuarios (1) ──→ (N) polizas
polizas  (1) ──→ (N) pagos
usuarios (1) ──→ (N) pagos
usuarios (1) ──→ (N) auditoria
```

---

## 🔗 Flujo de Datos en Endpoints

### 1. **Crear Usuario**
```
POST /api/v1/usuarios/
```
- ✅ Guarda en **MySQL** (`usuarios`)
- ✅ Registra en **MySQL** (`auditoria`)

**Por qué**: Necesita email único y relaciones FK

---

### 2. **Listar Seguros**
```
GET /api/v1/seguros/
```
- ✅ Lee de **MongoDB** (`seguros`)

**Por qué**: Catálogo flexible sin relaciones complejas

---

### 3. **Comprar Seguro**
```
POST /api/v1/usuarios/{usuario_id}/comprar-seguro
```
**Sistema Híbrido**:
1. Lee usuario de **MySQL** (`usuarios`) ✅
2. Lee seguro de **MongoDB** (`seguros`) ✅
3. Valida saldo en **MySQL**
4. Crea póliza en **MySQL** (`polizas`) ✅
5. Actualiza saldo en **MySQL** (`usuarios`) ✅
6. Registra auditoría en **MySQL** (`auditoria`) ✅

**Por qué**: Combina flexibilidad del catálogo (MongoDB) con integridad transaccional (MySQL)

---

### 4. **Pagar Cuota**
```
POST /api/v1/polizas/{poliza_id}/pagar-cuota
```
- ✅ Lee póliza de **MySQL** (`polizas`)
- ✅ Verifica usuario en **MySQL** (`usuarios`)
- ✅ Registra pago en **MySQL** (`pagos`)
- ✅ Actualiza saldo en **MySQL** (`usuarios`)
- ✅ Auditoría en **MySQL** (`auditoria`)

**Por qué**: Transacción financiera requiere ACID

---

### 5. **Ver Próximos Pagos**
```
GET /api/v1/usuarios/{usuario_id}/proximos-pagos
```
**Sistema Híbrido**:
1. Lee pólizas de **MySQL** (`polizas`) ✅
2. Por cada póliza, busca seguro en **MongoDB** (`seguros`) ✅
3. Combina información y devuelve

**Por qué**: Une datos transaccionales (MySQL) con catálogo (MongoDB)

---

## 📁 Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `app/database.py` | Conexión a **MongoDB** |
| `app/database_sql.py` | Conexión a **MySQL** |
| `app/models.py` | Modelos Pydantic (MongoDB) |
| `app/models_sql.py` | Modelos SQLAlchemy (MySQL) |
| `app/crud.py` | Operaciones MongoDB |
| `app/crud_sql.py` | Operaciones MySQL |
| `app/routes.py` | Endpoints (usa ambas DBs) |

---

## 🎯 Ventajas del Sistema Híbrido

### ✅ Flexibilidad
- Agregar campos a seguros sin alterar esquema MySQL
- Catálogo puede crecer dinámicamente

### ✅ Integridad
- Relaciones FK garantizan consistencia
- Transacciones MySQL protegen pagos

### ✅ Performance
- MongoDB: Rápido para consultas de catálogo
- MySQL: Optimizado para JOINs y agregaciones

### ✅ Auditoría
- Todos los cambios críticos se registran en MySQL
- Historial completo de transacciones

---

## 🔧 Configuración

### MongoDB
```python
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "seguros_db"
```

### MySQL
```python
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "seguros_db_sql"
```

---

## 🧪 Comandos de Prueba

### Ver datos en MongoDB
```bash
mongo
use seguros_db
db.seguros.find().pretty()
```

### Ver datos en MySQL
```bash
mysql -u root
USE seguros_db_sql;
SELECT * FROM usuarios;
SELECT * FROM polizas;
SELECT * FROM pagos;
SELECT * FROM auditoria;
```

---

## 📊 Estado Actual

### MongoDB
- ✅ 3-5 seguros (Básico, Estándar, Premium + tests)
- ✅ Conexión activa

### MySQL
- ✅ 5 tablas creadas
- ✅ Relaciones FK configuradas
- ✅ Conexión activa
- ⚠️ Sin datos iniciales (se crean al usar endpoints)

---

## 🚀 Próximos Pasos

1. **Probar endpoints** con Postman/frontend
2. **Migrar usuarios existentes** de MongoDB a MySQL (opcional)
3. **Optimizar consultas** con índices
4. **Agregar cache** (Redis) para seguros frecuentes

---

## 📝 Notas Importantes

- **No hay sincronización automática**: MongoDB y MySQL son independientes
- **Seguros solo en MongoDB**: No se duplican en MySQL (solo ID se guarda)
- **Usuarios solo en MySQL**: Nueva arquitectura no usa MongoDB para usuarios
- **Auditoría completa**: Todos los cambios en MySQL se registran

---

**Versión**: 1.0 (Sistema Híbrido)  
**Última actualización**: 30 Nov 2025
