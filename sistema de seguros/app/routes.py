from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from . import crud, models, schemas, database
from . import crud_sql, database_sql

router = APIRouter()

# Routes para Seguros
@router.get("/seguros/", response_model=List[schemas.Seguro])
async def listar_seguros(
    skip: int = 0,
    limit: int = 10,
    db: AsyncIOMotorDatabase = Depends(database.get_db)
):
    """Obtener todos los seguros disponibles"""
    return await crud.obtener_seguros(db, skip=skip, limit=limit)

@router.get("/seguros/economicos/{tipo}", response_model=List[schemas.Seguro])
async def listar_seguros_por_tipo(tipo: str, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Obtener seguros por tipo (basico, estandar, premium)"""
    if tipo not in ["basico", "estandar", "premium"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser: basico, estandar o premium")
    
    seguros = await crud.obtener_seguros_economicos(db, tipo=tipo)
    return seguros

@router.post("/seguros/economicos/", response_model=schemas.Seguro)
async def crear_seguro_economico(seguro: schemas.SeguroCreate, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Crear un nuevo seguro económico (para administradores)"""
    return await crud.crear_seguro_economico(db, seguro)


# Rutas para Usuarios (AHORA USA MYSQL)
@router.post("/usuarios/", response_model=schemas.Usuario)
async def crear_usuario(
    usuario: schemas.UsuarioCreate, 
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """Crear un nuevo usuario en MySQL"""
    # Verificar que el email no exista
    usuario_existente = await crud_sql.obtener_usuario_por_email_sql(db_sql, usuario.email)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear usuario en MySQL
    db_usuario = await crud_sql.crear_usuario_sql(db_sql, usuario)
    
    # Convertir a schema Pydantic
    return schemas.Usuario(
        id=db_usuario.id,
        nombre=db_usuario.nombre,
        email=db_usuario.email,
        telefono=db_usuario.telefono,
        saldo=float(db_usuario.saldo),
        activo=db_usuario.activo,
        fecha_registro=db_usuario.fecha_registro
    )


@router.get("/usuarios/", response_model=List[schemas.Usuario])
async def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """Listar todos los usuarios desde MySQL"""
    usuarios = await crud_sql.obtener_usuarios_sql(db_sql, skip=skip, limit=limit)
    
    return [
        schemas.Usuario(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            telefono=u.telefono,
            saldo=float(u.saldo),
            activo=u.activo,
            fecha_registro=u.fecha_registro
        )
        for u in usuarios
    ]


@router.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
async def obtener_usuario(
    usuario_id: str,
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """Obtener información de un usuario desde MySQL"""
    usuario = await crud_sql.obtener_usuario_sql(db_sql, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return schemas.Usuario(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        saldo=float(usuario.saldo),
        activo=usuario.activo,
        fecha_registro=usuario.fecha_registro
    )

# Routes para Compra y Pagos (SISTEMA HÍBRIDO: MySQL + MongoDB)
@router.post("/usuarios/{usuario_id}/comprar-seguro")
async def comprar_seguro(
    usuario_id: str, 
    compra: schemas.CompraSeguroRequest, 
    db_mongo: AsyncIOMotorDatabase = Depends(database.get_db),
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """
    Comprar un paquete de seguro (pago inicial)
    - Usuario y Póliza: MySQL
    - Seguro: MongoDB
    """
    # 1. Obtener usuario de MySQL
    usuario = await crud_sql.obtener_usuario_sql(db_sql, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # 2. Obtener seguro de MongoDB
    seguro = await db_mongo.seguros.find_one({"id": compra.seguro_id, "activo": True})
    if not seguro:
        raise HTTPException(status_code=404, detail="Seguro no encontrado")
    
    # 3. Verificar saldo suficiente
    if usuario.saldo < seguro["precio"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Saldo insuficiente. Necesitas ${seguro['precio']}, tienes ${usuario.saldo}"
        )
    
    # 4. Descontar pago inicial del saldo
    nuevo_saldo = float(usuario.saldo) - seguro["precio"]
    await crud_sql.actualizar_saldo_usuario_sql(db_sql, usuario_id, nuevo_saldo)
    
    # 5. Crear póliza en MySQL
    poliza = await crud_sql.crear_poliza_sql(
        db_sql,
        usuario_id=usuario_id,
        seguro_id=compra.seguro_id,
        monto_total=seguro["precio"],
        cuota_mensual=seguro["cuota_mensual"],
        duracion_meses=seguro["duracion_meses"]
    )
    
    return {
        "mensaje": "Seguro comprado exitosamente",
        "poliza_id": poliza.id,
        "seguro_nombre": seguro["nombre"],
        "monto_pagado": seguro["precio"],
        "nuevo_saldo": nuevo_saldo,
        "cuota_mensual": seguro["cuota_mensual"],
        "cuotas_totales": seguro["duracion_meses"]
    }

@router.post("/polizas/{poliza_id}/pagar-cuota")
async def pagar_cuota_mensual(
    poliza_id: str, 
    pago: schemas.PagoCuotaRequest,
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """
    Pagar la cuota mensual de una póliza
    - Póliza, Usuario, Pago: MySQL
    """
    # 1. Obtener póliza con sus relaciones
    poliza = await crud_sql.obtener_poliza_sql(db_sql, poliza_id)
    if not poliza:
        raise HTTPException(status_code=404, detail="Póliza no encontrada")
    
    # 2. Verificar si ya pagó todas las cuotas
    if poliza.cuotas_pagadas >= poliza.cuotas_totales:
        raise HTTPException(status_code=400, detail="Ya se pagaron todas las cuotas de esta póliza")
    
    # 3. Obtener usuario
    usuario = await crud_sql.obtener_usuario_sql(db_sql, poliza.usuario_id)
    
    # 4. Verificar saldo suficiente
    if usuario.saldo < poliza.cuota_mensual:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Necesitas ${poliza.cuota_mensual}, tienes ${usuario.saldo}"
        )
    
    # 5. Descontar cuota del saldo
    nuevo_saldo = float(usuario.saldo) - float(poliza.cuota_mensual)
    await crud_sql.actualizar_saldo_usuario_sql(db_sql, poliza.usuario_id, nuevo_saldo)
    
    # 6. Registrar pago
    numero_cuota = poliza.cuotas_pagadas + 1
    pago_registro = await crud_sql.crear_pago_sql(
        db_sql,
        poliza_id=poliza_id,
        usuario_id=poliza.usuario_id,
        monto=float(poliza.cuota_mensual),
        numero_cuota=numero_cuota
    )
    
    # 7. Actualizar cuotas pagadas en póliza
    poliza_actualizada = await crud_sql.actualizar_cuotas_poliza_sql(db_sql, poliza_id)
    
    return {
        "mensaje": "Cuota pagada exitosamente",
        "pago_id": pago_registro.id,
        "numero_cuota": numero_cuota,
        "monto_pagado": float(poliza.cuota_mensual),
        "nuevo_saldo": nuevo_saldo,
        "cuotas_pagadas": poliza_actualizada.cuotas_pagadas,
        "cuotas_totales": poliza_actualizada.cuotas_totales,
        "estado_poliza": poliza_actualizada.estado.value
    }

@router.get("/usuarios/{usuario_id}/proximos-pagos")
async def obtener_proximos_pagos(
    usuario_id: str,
    db_mongo: AsyncIOMotorDatabase = Depends(database.get_db),
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """
    Obtener las pólizas activas del usuario con pagos pendientes
    - Pólizas: MySQL
    - Seguros: MongoDB
    """
    # 1. Obtener pólizas del usuario desde MySQL
    polizas = await crud_sql.obtener_polizas_usuario_sql(db_sql, usuario_id)
    
    resultado = []
    for poliza in polizas:
        # Solo incluir pólizas activas con cuotas pendientes
        if poliza.estado.value == "activa" and poliza.cuotas_pagadas < poliza.cuotas_totales:
            # 2. Obtener información del seguro desde MongoDB
            seguro = await db_mongo.seguros.find_one({"id": poliza.seguro_id})
            
            if seguro:
                cuotas_pendientes = poliza.cuotas_totales - poliza.cuotas_pagadas
                resultado.append({
                    "poliza_id": poliza.id,
                    "seguro_nombre": seguro["nombre"],
                    "seguro_tipo": seguro.get("tipo", ""),
                    "cuota_mensual": float(poliza.cuota_mensual),
                    "cuotas_pagadas": poliza.cuotas_pagadas,
                    "cuotas_totales": poliza.cuotas_totales,
                    "cuotas_pendientes": cuotas_pendientes,
                    "fecha_inicio": poliza.fecha_inicio.isoformat(),
                    "fecha_fin": poliza.fecha_fin.isoformat() if poliza.fecha_fin else None
                })
    
    return {
        "usuario_id": usuario_id,
        "total_polizas_activas": len(resultado),
        "proximos_pagos": resultado
    }


@router.get("/usuarios/{usuario_id}/polizas")
async def obtener_polizas_usuario(
    usuario_id: str,
    db_mongo: AsyncIOMotorDatabase = Depends(database.get_db),
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """Obtener todas las pólizas de un usuario (activas, vencidas, canceladas)"""
    polizas = await crud_sql.obtener_polizas_usuario_sql(db_sql, usuario_id)
    
    resultado = []
    for poliza in polizas:
        seguro = await db_mongo.seguros.find_one({"id": poliza.seguro_id})
        
        if seguro:
            resultado.append({
                "poliza_id": poliza.id,
                "seguro_nombre": seguro["nombre"],
                "seguro_tipo": seguro.get("tipo", ""),
                "estado": poliza.estado.value,
                "monto_total": float(poliza.monto_total),
                "cuota_mensual": float(poliza.cuota_mensual),
                "cuotas_pagadas": poliza.cuotas_pagadas,
                "cuotas_totales": poliza.cuotas_totales,
                "fecha_inicio": poliza.fecha_inicio.isoformat(),
                "fecha_fin": poliza.fecha_fin.isoformat() if poliza.fecha_fin else None
            })
    
    return {
        "usuario_id": usuario_id,
        "total_polizas": len(resultado),
        "polizas": resultado
    }


@router.get("/polizas/{poliza_id}/pagos")
async def obtener_historial_pagos(
    poliza_id: str,
    db_sql: AsyncSession = Depends(database_sql.get_db_sql)
):
    """Obtener historial de pagos de una póliza"""
    pagos = await crud_sql.obtener_pagos_poliza_sql(db_sql, poliza_id)
    
    return {
        "poliza_id": poliza_id,
        "total_pagos": len(pagos),
        "pagos": [
            {
                "pago_id": pago.id,
                "monto": float(pago.monto),
                "fecha_pago": pago.fecha_pago.isoformat(),
                "numero_cuota": pago.numero_cuota,
                "metodo_pago": pago.metodo_pago,
                "estado": pago.estado.value
            }
            for pago in pagos
        ]
    }

# Mantener todas las rutas anteriores...