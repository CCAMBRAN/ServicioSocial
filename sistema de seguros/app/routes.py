from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from . import crud, models, schemas, database

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


# Rutas para Usuarios
@router.post("/usuarios/", response_model=schemas.Usuario)
async def crear_usuario(usuario: schemas.UsuarioCreate, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Crear un nuevo usuario"""
    return await crud.crear_usuario(db, usuario)

# Routes para Compra y Pagos
@router.post("/usuarios/{usuario_id}/comprar-seguro")
async def comprar_seguro(usuario_id: str, compra: schemas.CompraSeguroRequest, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Comprar un paquete de seguro (pago inicial)"""
    poliza, seguro, mensaje = await crud.comprar_seguro(db, usuario_id=usuario_id, seguro_id=compra.seguro_id)
    if not poliza:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return {
        "mensaje": mensaje,
        "poliza_id": poliza["id"],
        "proximo_pago": poliza["proximo_pago"],
        "cuota_mensual": seguro["cuota_mensual"]
    }

@router.post("/polizas/{poliza_id}/pagar-cuota")
async def pagar_cuota_mensual(poliza_id: str, pago: schemas.PagoCuotaRequest, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Pagar la cuota mensual de una póliza"""
    poliza, mensaje = await crud.pagar_cuota_mensual(db, poliza_id=poliza_id, metodo_pago=pago.metodo_pago)
    if not poliza:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return {
        "mensaje": mensaje,
        "pagos_realizados": poliza["pagos_realizados"],
        "total_pagos": poliza["total_pagos"],
        "proximo_pago": poliza["proximo_pago"]
    }

@router.get("/usuarios/{usuario_id}/proximos-pagos")
async def obtener_proximos_pagos(usuario_id: str, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    """Obtener los próximos pagos pendientes del usuario"""
    polizas = await crud.obtener_proximos_pagos_usuario(db, usuario_id)
    resultado = []
    for poliza in polizas:
        seguro = await db.seguros.find_one({"id": poliza.get("seguro_id")})
        if seguro:
            resultado.append({
                "poliza_id": poliza["id"],
                "seguro_nombre": seguro["nombre"],
                "cuota_mensual": seguro["cuota_mensual"],
                "proximo_pago": poliza["proximo_pago"],
                "pagos_realizados": poliza["pagos_realizados"],
                "total_pagos": poliza["total_pagos"]
            })
    return {"proximos_pagos": resultado}

# Mantener todas las rutas anteriores...