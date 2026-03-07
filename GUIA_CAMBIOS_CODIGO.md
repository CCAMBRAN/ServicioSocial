# 🔧 Guía Práctica de Cambios de Código

## 1️⃣ CAMBIOS EN `app/schemas.py`

### Antes (actual):
```python
class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: str
    saldo: float
    fecha_registro: datetime
    activo: bool
```

### Después (nuevo):
```python
from typing import Literal, Optional

class UsuarioCreate(UsuarioBase):
    tipo_usuario: Literal["fondeador", "beneficiario"]  # ← NUEVO

class Usuario(UsuarioBase):
    id: str
    tipo_usuario: Literal["fondeador", "beneficiario"]  # ← NUEVO
    saldo: float
    fecha_registro: datetime
    activo: bool
    datos_adicionales: Optional[dict] = None  # ← OPCIONAL
```

---

## 2️⃣ CAMBIOS EN `app/crud.py`

### Función: Crear Usuario (NUEVA)
```python
async def crear_usuario_mongo(
    db: AsyncIOMotorDatabase, 
    usuario: schemas.UsuarioCreate
) -> dict:
    """Crear un usuario (fondeador o beneficiario) en MongoDB"""
    
    # Verificar que no exista email
    usuario_existente = await db.usuarios.find_one({"email": usuario.email})
    if usuario_existente:
        raise ValueError(f"Email {usuario.email} ya está registrado")
    
    # Crear documento
    nuevo_usuario = {
        "id": str(uuid.uuid4()),
        "nombre": usuario.nombre,
        "email": usuario.email,
        "telefono": usuario.telefono,
        "tipo_usuario": usuario.tipo_usuario,  # ← fondeador o beneficiario
        "saldo": 500.00,  # Saldo inicial
        "activo": True,
        "fecha_registro": datetime.datetime.utcnow(),
        "datos_adicionales": {}
    }
    
    # Insertar en MongoDB
    result = await db.usuarios.insert_one(nuevo_usuario)
    nuevo_usuario["_id"] = result.inserted_id
    
    # Registrar auditoría
    await registrar_auditoria_mongo(
        db,
        usuario_id=nuevo_usuario["id"],
        accion="CREATE",
        tabla_afectada="usuarios",
        registro_id=nuevo_usuario["id"],
        datos_nuevos={"nombre": usuario.nombre, "email": usuario.email}
    )
    
    return nuevo_usuario


async def obtener_usuario_mongo(
    db: AsyncIOMotorDatabase, 
    usuario_id: str
) -> Optional[dict]:
    """Obtener usuario por ID"""
    return await db.usuarios.find_one({"id": usuario_id})


async def obtener_usuario_por_email_mongo(
    db: AsyncIOMotorDatabase, 
    email: str
) -> Optional[dict]:
    """Obtener usuario por email"""
    return await db.usuarios.find_one({"email": email})


async def obtener_usuarios_por_tipo(
    db: AsyncIOMotorDatabase, 
    tipo: Literal["fondeador", "beneficiario"],
    skip: int = 0,
    limit: int = 100
) -> list:
    """Obtener usuarios por tipo (fondeador o beneficiario)"""
    cursor = db.usuarios.find({
        "tipo_usuario": tipo,
        "activo": True
    }).skip(skip).limit(limit)
    
    return [doc async for doc in cursor]
```

### Función: Actualizar Saldo (ACTUALIZADA)
```python
async def actualizar_saldo_usuario_mongo(
    db: AsyncIOMotorDatabase, 
    usuario_id: str, 
    nuevo_saldo: float
) -> dict:
    """Actualizar saldo de un usuario"""
    
    usuario = await db.usuarios.find_one({"id": usuario_id})
    if not usuario:
        raise ValueError(f"Usuario {usuario_id} no encontrado")
    
    saldo_anterior = usuario.get("saldo", 0)
    
    # Actualizar
    result = await db.usuarios.update_one(
        {"id": usuario_id},
        {"$set": {"saldo": nuevo_saldo}}
    )
    
    if result.modified_count == 0:
        raise ValueError("No se pudo actualizar el saldo")
    
    # Auditoría
    await registrar_auditoria_mongo(
        db,
        usuario_id=usuario_id,
        accion="UPDATE_SALDO",
        tabla_afectada="usuarios",
        registro_id=usuario_id,
        datos_anteriores={"saldo": saldo_anterior},
        datos_nuevos={"saldo": nuevo_saldo}
    )
    
    return await db.usuarios.find_one({"id": usuario_id})
```

### Función: Crear Póliza (ACTUALIZADA - IMPORTANTE)
```python
async def crear_poliza_mongo(
    db: AsyncIOMotorDatabase,
    beneficiario_id: str,
    seguro_id: str,
    fondeador_id: Optional[str] = None
) -> dict:
    """
    Crear una póliza de seguro
    
    Args:
        beneficiario_id: Usuario que recibe el seguro
        seguro_id: Seguro a comprar
        fondeador_id: Usuario que paga (opcional)
    """
    
    # Validar beneficiario
    beneficiario = await db.usuarios.find_one({"id": beneficiario_id})
    if not beneficiario:
        raise ValueError(f"Beneficiario {beneficiario_id} no encontrado")
    if beneficiario["tipo_usuario"] != "beneficiario":
        raise ValueError("El usuario debe ser tipo 'beneficiario'")
    
    # Validar fondeador (si se proporciona)
    if fondeador_id:
        fondeador = await db.usuarios.find_one({"id": fondeador_id})
        if not fondeador:
            raise ValueError(f"Fondeador {fondeador_id} no encontrado")
        if fondeador["tipo_usuario"] != "fondeador":
            raise ValueError("El usuario debe ser tipo 'fondeador'")
    
    # Obtener seguro
    seguro = await db.seguros.find_one({"id": seguro_id, "activo": True})
    if not seguro:
        raise ValueError(f"Seguro {seguro_id} no encontrado")
    
    # Crear póliza
    poliza = {
        "id": str(uuid.uuid4()),
        "beneficiario_id": beneficiario_id,  # ← NUEVO
        "fondeador_id": fondeador_id,         # ← NUEVO (puede ser None)
        "seguro_id": seguro_id,
        "estado": "activa",
        "fecha_inicio": datetime.datetime.utcnow(),
        "fecha_fin": datetime.datetime.utcnow() + datetime.timedelta(
            days=seguro["duracion_meses"] * 30
        ),
        "monto_total": seguro["precio"],
        "cuota_mensual": seguro["cuota_mensual"],
        "cuotas_pagadas": 0,
        "cuotas_totales": seguro["duracion_meses"],
        "proxima_cuota": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    
    result = await db.polizas.insert_one(poliza)
    poliza["_id"] = result.inserted_id
    
    # Registrar auditoría
    await registrar_auditoria_mongo(
        db,
        usuario_id=beneficiario_id,
        accion="CREATE",
        tabla_afectada="polizas",
        registro_id=poliza["id"],
        datos_nuevos={
            "beneficiario_id": beneficiario_id,
            "fondeador_id": fondeador_id,
            "seguro_id": seguro_id
        }
    )
    
    return poliza
```

### Función: Crear Pago (ACTUALIZADA - IMPORTANTE)
```python
async def crear_pago_mongo(
    db: AsyncIOMotorDatabase,
    poliza_id: str,
    usuario_pagador_id: str,  # ← NUEVO: quién paga
    monto: float,
    numero_cuota: int,
    tipo_pago: Literal["inicial", "cuota_mensual"] = "cuota_mensual"
) -> dict:
    """
    Registrar un pago de póliza
    
    Args:
        poliza_id: ID de la póliza
        usuario_pagador_id: Usuario que realiza el pago
        monto: Monto a pagar
        numero_cuota: Número de cuota
        tipo_pago: Tipo de pago (inicial o cuota_mensual)
    """
    
    # Validar póliza
    poliza = await db.polizas.find_one({"id": poliza_id})
    if not poliza:
        raise ValueError(f"Póliza {poliza_id} no encontrada")
    
    # Validar usuario pagador
    usuario_pagador = await db.usuarios.find_one({"id": usuario_pagador_id})
    if not usuario_pagador:
        raise ValueError(f"Usuario pagador {usuario_pagador_id} no encontrado")
    
    # Verificar saldo
    if usuario_pagador.get("saldo", 0) < monto:
        raise ValueError(
            f"Saldo insuficiente. Necesitas ${monto}, tienes ${usuario_pagador.get('saldo', 0)}"
        )
    
    # Descontar saldo
    await actualizar_saldo_usuario_mongo(
        db,
        usuario_pagador_id,
        usuario_pagador.get("saldo", 0) - monto
    )
    
    # Crear pago
    pago = {
        "id": str(uuid.uuid4()),
        "poliza_id": poliza_id,
        "usuario_pagador_id": usuario_pagador_id,  # ← NUEVO
        "monto": monto,
        "fecha_pago": datetime.datetime.utcnow(),
        "numero_cuota": numero_cuota,
        "metodo_pago": "saldo",
        "estado": "completado",
        "tipo_pago": tipo_pago  # ← NUEVO
    }
    
    result = await db.pagos.insert_one(pago)
    pago["_id"] = result.inserted_id
    
    # Actualizar cuotas pagadas en póliza
    await db.polizas.update_one(
        {"id": poliza_id},
        {"$inc": {"cuotas_pagadas": 1}}
    )
    
    # Registrar auditoría
    await registrar_auditoria_mongo(
        db,
        usuario_id=usuario_pagador_id,
        accion="CREATE_PAGO",
        tabla_afectada="pagos",
        registro_id=pago["id"],
        datos_nuevos={
            "poliza_id": poliza_id,
            "usuario_pagador_id": usuario_pagador_id,
            "monto": monto
        }
    )
    
    return pago


async def registrar_auditoria_mongo(
    db: AsyncIOMotorDatabase,
    usuario_id: Optional[str],
    accion: str,
    tabla_afectada: str,
    registro_id: str,
    datos_anteriores: Optional[dict] = None,
    datos_nuevos: Optional[dict] = None
) -> dict:
    """Registrar acción en auditoría"""
    
    auditoria = {
        "usuario_id": usuario_id,
        "accion": accion,
        "tabla_afectada": tabla_afectada,
        "registro_id": registro_id,
        "datos_anteriores": datos_anteriores or {},
        "datos_nuevos": datos_nuevos or {},
        "timestamp": datetime.datetime.utcnow()
    }
    
    result = await db.auditoria.insert_one(auditoria)
    auditoria["_id"] = result.inserted_id
    
    return auditoria
```

---

## 3️⃣ CAMBIOS EN `app/routes.py`

### Endpoint: Crear Usuario (ACTUALIZADO)
```python
@router.post("/usuarios/", response_model=schemas.Usuario)
async def crear_usuario(
    usuario: schemas.UsuarioCreate,
    db: AsyncIOMotorDatabase = Depends(database.get_db)
):
    """
    Crear un nuevo usuario (fondeador o beneficiario)
    
    Body:
    {
        "nombre": "Juan",
        "email": "juan@example.com",
        "telefono": "123456",
        "tipo_usuario": "fondeador"  ← NUEVO
    }
    """
    try:
        db_usuario = await crud.crear_usuario_mongo(db, usuario)
        
        return schemas.Usuario(
            id=db_usuario["id"],
            nombre=db_usuario["nombre"],
            email=db_usuario["email"],
            telefono=db_usuario["telefono"],
            tipo_usuario=db_usuario["tipo_usuario"],  # ← NUEVO
            saldo=db_usuario["saldo"],
            activo=db_usuario["activo"],
            fecha_registro=db_usuario["fecha_registro"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usuarios/tipo/{tipo}")
async def listar_usuarios_por_tipo(
    tipo: Literal["fondeador", "beneficiario"],
    skip: int = 0,
    limit: int = 100,
    db: AsyncIOMotorDatabase = Depends(database.get_db)
):
    """Listar usuarios por tipo (fondeador o beneficiario)"""
    try:
        usuarios = await crud.obtener_usuarios_por_tipo(db, tipo, skip, limit)
        
        return [
            schemas.Usuario(
                id=u["id"],
                nombre=u["nombre"],
                email=u["email"],
                telefono=u["telefono"],
                tipo_usuario=u["tipo_usuario"],
                saldo=u["saldo"],
                activo=u["activo"],
                fecha_registro=u["fecha_registro"]
            )
            for u in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Endpoint: Comprar Seguro (ACTUALIZADO - IMPORTANTE)
```python
@router.post("/usuarios/{beneficiario_id}/comprar-seguro")
async def comprar_seguro(
    beneficiario_id: str,
    compra: schemas.CompraSeguroRequest,
    db: AsyncIOMotorDatabase = Depends(database.get_db)
):
    """
    Comprar un seguro para un beneficiario
    
    Body:
    {
        "seguro_id": "seguro-123",
        "fondeador_id": "fondeador-456"  ← NUEVO (opcional)
    }
    """
    try:
        # Crear póliza
        poliza = await crud.crear_poliza_mongo(
            db,
            beneficiario_id=beneficiario_id,
            seguro_id=compra.seguro_id,
            fondeador_id=compra.fondeador_id  # ← NUEVO
        )
        
        # Procesar pago inicial
        seguro = await db.seguros.find_one({"id": compra.seguro_id})
        
        # Paga el beneficiario o el fondeador
        usuario_pagador_id = compra.fondeador_id or beneficiario_id
        
        pago = await crud.crear_pago_mongo(
            db,
            poliza_id=poliza["id"],
            usuario_pagador_id=usuario_pagador_id,
            monto=seguro["precio"],
            numero_cuota=1,
            tipo_pago="inicial"
        )
        
        return {
            "mensaje": "Seguro comprado exitosamente",
            "poliza_id": poliza["id"],
            "beneficiario_id": beneficiario_id,
            "fondeador_id": compra.fondeador_id,
            "seguro_nombre": seguro["nombre"],
            "monto_pagado": seguro["precio"],
            "usuario_pagador_id": usuario_pagador_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 4️⃣ ELIMINAR ESTOS ARCHIVOS

```bash
# En PowerShell:
Remove-Item -Path ".\app\models_sql.py"
Remove-Item -Path ".\app\database_sql.py"
Remove-Item -Path ".\app\crud_sql.py"
```

---

## 5️⃣ ACTUALIZAR `main.py`

### Antes:
```python
from app import database_sql, database

@app.on_event("startup")
async def startup_event():
    await database.connect_to_mongo()
    # No necesita SQL
```

### Después:
```python
from app import database

@app.on_event("startup")
async def startup_event():
    await database.connect_to_mongo()
    # Solo MongoDB

@app.on_event("shutdown")
async def shutdown_event():
    await database.close_mongo_connection()
```

---

## ✅ Checklist de Implementación

- [ ] Actualizar `schemas.py` con `tipo_usuario`
- [ ] Actualizar `crud.py` con funciones de MongoDB
- [ ] Actualizar `routes.py` con nuevos endpoints
- [ ] Eliminar `models_sql.py`
- [ ] Eliminar `database_sql.py`
- [ ] Eliminar `crud_sql.py`
- [ ] Actualizar imports en todos los archivos
- [ ] Crear índices en MongoDB
- [ ] Probar endpoints con Postman

