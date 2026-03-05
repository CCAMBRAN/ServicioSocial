"""
Operaciones CRUD para MySQL usando SQLAlchemy (async)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from app.models_sql import UsuarioSQL, SeguroSQL, PolizaSQL, PagoSQL, AuditoriaSQL, EstadoPoliza, EstadoPago
from app import schemas
from typing import List, Optional
from datetime import datetime, timedelta
import uuid


# ============================================
# CRUD: Usuarios
# ============================================

async def crear_usuario_sql(db: AsyncSession, usuario: schemas.UsuarioCreate) -> UsuarioSQL:
    """Crear un nuevo usuario en MySQL"""
    db_usuario = UsuarioSQL(
        id=str(uuid.uuid4()),
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        saldo=500.00,
        activo=True
    )
    db.add(db_usuario)
    await db.commit()
    await db.refresh(db_usuario)
    
    # Registrar en auditoría
    await crear_auditoria_sql(
        db, 
        usuario_id=db_usuario.id,
        accion="CREATE",
        tabla="usuarios",
        registro_id=db_usuario.id,
        datos_nuevos={"nombre": usuario.nombre, "email": usuario.email}
    )
    
    return db_usuario


async def obtener_usuario_sql(db: AsyncSession, usuario_id: str) -> Optional[UsuarioSQL]:
    """Obtener un usuario por ID"""
    result = await db.execute(
        select(UsuarioSQL).where(UsuarioSQL.id == usuario_id)
    )
    return result.scalar_one_or_none()


async def obtener_usuario_por_email_sql(db: AsyncSession, email: str) -> Optional[UsuarioSQL]:
    """Obtener un usuario por email"""
    result = await db.execute(
        select(UsuarioSQL).where(UsuarioSQL.email == email)
    )
    return result.scalar_one_or_none()


async def obtener_usuarios_sql(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[UsuarioSQL]:
    """Obtener lista de usuarios"""
    result = await db.execute(
        select(UsuarioSQL).where(UsuarioSQL.activo == True).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def actualizar_saldo_usuario_sql(db: AsyncSession, usuario_id: str, nuevo_saldo: float) -> UsuarioSQL:
    """Actualizar el saldo de un usuario"""
    usuario = await obtener_usuario_sql(db, usuario_id)
    if usuario:
        saldo_anterior = usuario.saldo
        usuario.saldo = nuevo_saldo
        await db.commit()
        await db.refresh(usuario)
        
        # Auditoría
        await crear_auditoria_sql(
            db,
            usuario_id=usuario_id,
            accion="UPDATE_SALDO",
            tabla="usuarios",
            registro_id=usuario_id,
            datos_anteriores={"saldo": float(saldo_anterior)},
            datos_nuevos={"saldo": nuevo_saldo}
        )
    return usuario


# ============================================
# CRUD: Seguros
# ============================================

async def crear_seguro_sql(db: AsyncSession, seguro: schemas.SeguroCreate) -> SeguroSQL:
    """Crear un nuevo seguro en MySQL"""
    db_seguro = SeguroSQL(
        id=str(uuid.uuid4()),
        nombre=seguro.nombre,
        descripcion=seguro.descripcion,
        tipo=seguro.tipo,
        precio=seguro.precio,
        cuota_mensual=seguro.cuota_mensual,
        cobertura=seguro.cobertura,
        duracion_meses=seguro.duracion_meses,
        activo=True
    )
    db.add(db_seguro)
    await db.commit()
    await db.refresh(db_seguro)
    return db_seguro


async def obtener_seguro_sql(db: AsyncSession, seguro_id: str) -> Optional[SeguroSQL]:
    """Obtener un seguro por ID"""
    result = await db.execute(
        select(SeguroSQL).where(SeguroSQL.id == seguro_id)
    )
    return result.scalar_one_or_none()


async def obtener_seguros_sql(db: AsyncSession) -> List[SeguroSQL]:
    """Obtener todos los seguros activos"""
    result = await db.execute(
        select(SeguroSQL).where(SeguroSQL.activo == True)
    )
    return result.scalars().all()


# ============================================
# CRUD: Pólizas
# ============================================

async def crear_poliza_sql(
    db: AsyncSession,
    usuario_id: str,
    seguro_id: str,
    monto_total: float,
    cuota_mensual: float,
    duracion_meses: int
) -> PolizaSQL:
    """Crear una nueva póliza"""
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=duracion_meses * 30)
    
    db_poliza = PolizaSQL(
        id=str(uuid.uuid4()),
        usuario_id=usuario_id,
        seguro_id=seguro_id,
        estado=EstadoPoliza.ACTIVA,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto_total=monto_total,
        cuota_mensual=cuota_mensual,
        cuotas_pagadas=0,
        cuotas_totales=duracion_meses
    )
    db.add(db_poliza)
    await db.commit()
    await db.refresh(db_poliza)
    
    # Auditoría
    await crear_auditoria_sql(
        db,
        usuario_id=usuario_id,
        accion="CREATE_POLIZA",
        tabla="polizas",
        registro_id=db_poliza.id,
        datos_nuevos={"seguro_id": seguro_id, "monto_total": monto_total}
    )
    
    return db_poliza


async def obtener_poliza_sql(db: AsyncSession, poliza_id: str) -> Optional[PolizaSQL]:
    """Obtener una póliza por ID con sus relaciones"""
    result = await db.execute(
        select(PolizaSQL)
        .options(selectinload(PolizaSQL.usuario), selectinload(PolizaSQL.seguro))
        .where(PolizaSQL.id == poliza_id)
    )
    return result.scalar_one_or_none()


async def obtener_polizas_usuario_sql(db: AsyncSession, usuario_id: str) -> List[PolizaSQL]:
    """Obtener todas las pólizas de un usuario"""
    result = await db.execute(
        select(PolizaSQL)
        .options(selectinload(PolizaSQL.seguro))
        .where(PolizaSQL.usuario_id == usuario_id)
        .order_by(PolizaSQL.fecha_inicio.desc())
    )
    return result.scalars().all()


async def actualizar_cuotas_poliza_sql(db: AsyncSession, poliza_id: str) -> PolizaSQL:
    """Incrementar el contador de cuotas pagadas"""
    poliza = await obtener_poliza_sql(db, poliza_id)
    if poliza:
        poliza.cuotas_pagadas += 1
        
        # Si se completaron todas las cuotas, marcar como vencida
        if poliza.cuotas_pagadas >= poliza.cuotas_totales:
            poliza.estado = EstadoPoliza.VENCIDA
        
        await db.commit()
        await db.refresh(poliza)
    return poliza


# ============================================
# CRUD: Pagos
# ============================================

async def crear_pago_sql(
    db: AsyncSession,
    poliza_id: str,
    usuario_id: str,
    monto: float,
    numero_cuota: int
) -> PagoSQL:
    """Registrar un pago de cuota"""
    db_pago = PagoSQL(
        id=str(uuid.uuid4()),
        poliza_id=poliza_id,
        usuario_id=usuario_id,
        monto=monto,
        metodo_pago="saldo",
        estado=EstadoPago.COMPLETADO,
        numero_cuota=numero_cuota
    )
    db.add(db_pago)
    await db.commit()
    await db.refresh(db_pago)
    
    # Auditoría
    await crear_auditoria_sql(
        db,
        usuario_id=usuario_id,
        accion="CREATE_PAGO",
        tabla="pagos",
        registro_id=db_pago.id,
        datos_nuevos={"poliza_id": poliza_id, "monto": monto, "cuota": numero_cuota}
    )
    
    return db_pago


async def obtener_pagos_poliza_sql(db: AsyncSession, poliza_id: str) -> List[PagoSQL]:
    """Obtener todos los pagos de una póliza"""
    result = await db.execute(
        select(PagoSQL)
        .where(PagoSQL.poliza_id == poliza_id)
        .order_by(PagoSQL.fecha_pago.desc())
    )
    return result.scalars().all()


async def obtener_pagos_usuario_sql(db: AsyncSession, usuario_id: str) -> List[PagoSQL]:
    """Obtener todos los pagos de un usuario"""
    result = await db.execute(
        select(PagoSQL)
        .where(PagoSQL.usuario_id == usuario_id)
        .order_by(PagoSQL.fecha_pago.desc())
    )
    return result.scalars().all()


# ============================================
# CRUD: Auditoría
# ============================================

async def crear_auditoria_sql(
    db: AsyncSession,
    usuario_id: str,
    accion: str,
    tabla: str,
    registro_id: str,
    datos_anteriores: dict = None,
    datos_nuevos: dict = None,
    ip_address: str = None
) -> AuditoriaSQL:
    """Crear un registro de auditoría"""
    db_auditoria = AuditoriaSQL(
        usuario_id=usuario_id,
        accion=accion,
        tabla_afectada=tabla,
        registro_id=registro_id,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        ip_address=ip_address
    )
    db.add(db_auditoria)
    await db.commit()
    return db_auditoria


async def obtener_auditoria_usuario_sql(db: AsyncSession, usuario_id: str, limit: int = 50) -> List[AuditoriaSQL]:
    """Obtener historial de auditoría de un usuario"""
    result = await db.execute(
        select(AuditoriaSQL)
        .where(AuditoriaSQL.usuario_id == usuario_id)
        .order_by(AuditoriaSQL.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def obtener_auditoria_tabla_sql(db: AsyncSession, tabla: str, limit: int = 100) -> List[AuditoriaSQL]:
    """Obtener auditoría por tabla"""
    result = await db.execute(
        select(AuditoriaSQL)
        .where(AuditoriaSQL.tabla_afectada == tabla)
        .order_by(AuditoriaSQL.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
