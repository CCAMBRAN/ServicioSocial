from motor.motor_asyncio import AsyncIOMotorDatabase
from . import models, schemas
import uuid
import datetime
from typing import List, Optional, Tuple, Any


# --- Helpers ---
def _to_dict(obj: Any) -> dict:
    """Convierte un Pydantic model a dict si el objeto lo permite."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


async def crear_seguro_economico(db: AsyncIOMotorDatabase, seguro: schemas.SeguroCreate) -> dict:
    data = _to_dict(seguro)
    # asegurar id y metadata
    data.setdefault("id", str(uuid.uuid4()))
    data.setdefault("activo", True)
    data.setdefault("fecha_creacion", datetime.datetime.utcnow())
    await db.seguros.insert_one(data)
    return data


async def obtener_seguros(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 10) -> List[dict]:
    cursor = db.seguros.find({"activo": True}).skip(skip).limit(limit)
    return [doc async for doc in cursor]


async def obtener_seguros_economicos(db: AsyncIOMotorDatabase, tipo: Optional[str] = None) -> List[dict]:
    filtro = {"activo": True}
    if tipo:
        filtro["tipo"] = tipo
    cursor = db.seguros.find(filtro)
    return [doc async for doc in cursor]


async def procesar_pago(db: AsyncIOMotorDatabase, usuario_id: str, monto: float) -> bool:
    # Intentar decrementar el saldo solo si hay saldo suficiente (operación atómica)
    result = await db.usuarios.update_one({"id": usuario_id, "saldo": {"$gte": monto}}, {"$inc": {"saldo": -monto}})
    return result.modified_count == 1


async def comprar_seguro(db: AsyncIOMotorDatabase, usuario_id: str, seguro_id: str) -> Tuple[Optional[dict], Optional[dict], str]:
    usuario = await db.usuarios.find_one({"id": usuario_id})
    seguro = await db.seguros.find_one({"id": seguro_id})

    if not usuario or not seguro:
        return None, None, "Usuario o seguro no encontrado"

    if usuario.get("saldo", 0) < seguro.get("precio", 0):
        return None, None, f"Saldo insuficiente. Necesitas ${seguro.get('precio', 0)}"

    fecha_actual = datetime.datetime.utcnow()
    fecha_vencimiento = fecha_actual + datetime.timedelta(days=seguro.get("duracion_meses", 0) * 30)
    proximo_pago = fecha_actual + datetime.timedelta(days=30)

    poliza = {
        "id": str(uuid.uuid4()),
        "usuario_id": usuario_id,
        "seguro_id": seguro_id,
        "estado": "activa",
        "fecha_compra": fecha_actual,
        "fecha_vencimiento": fecha_vencimiento,
        "proximo_pago": proximo_pago,
        "total_pagos": seguro.get("duracion_meses", 0),
        "pagos_realizados": 0
    }

    # Procesar pago inicial
    ok = await procesar_pago(db, usuario_id, seguro.get("precio", 0))
    if not ok:
        return None, None, "Error al procesar el pago inicial"

    pago_paquete = {
        "id": str(uuid.uuid4()),
        "poliza_id": poliza["id"],
        "monto": seguro.get("precio", 0),
        "metodo_pago": "saldo",
        "estado": "completado",
        "fecha_pago": datetime.datetime.utcnow()
    }

    await db.polizas.insert_one(poliza)
    await db.pagos.insert_one(pago_paquete)

    return poliza, seguro, "Seguro comprado exitosamente. Ahora puedes comenzar con los pagos mensuales."


async def pagar_cuota_mensual(db: AsyncIOMotorDatabase, poliza_id: str, metodo_pago: str = "saldo") -> Tuple[Optional[dict], str]:
    poliza = await db.polizas.find_one({"id": poliza_id})
    if not poliza or poliza.get("estado") != "activa":
        return None, "Póliza no encontrada o inactiva"

    if poliza.get("pagos_realizados", 0) >= poliza.get("total_pagos", 0):
        return None, "Ya has completado todos los pagos de esta póliza"

    seguro = await db.seguros.find_one({"id": poliza.get("seguro_id")})
    usuario = await db.usuarios.find_one({"id": poliza.get("usuario_id")})

    if metodo_pago == "saldo":
        if not usuario or usuario.get("saldo", 0) < seguro.get("cuota_mensual", 0):
            return None, f"Saldo insuficiente. Necesitas ${seguro.get('cuota_mensual', 0)}"
        ok = await procesar_pago(db, usuario.get("id"), seguro.get("cuota_mensual", 0))
        if not ok:
            return None, "Error al procesar el pago"

    pago = {
        "id": str(uuid.uuid4()),
        "poliza_id": poliza_id,
        "monto": seguro.get("cuota_mensual", 0),
        "metodo_pago": metodo_pago,
        "estado": "completado",
        "fecha_pago": datetime.datetime.utcnow()
    }

    # Actualizar póliza
    nueva_pagos = poliza.get("pagos_realizados", 0) + 1
    proximo_pago = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    update = {"$set": {"pagos_realizados": nueva_pagos, "proximo_pago": proximo_pago}}
    if nueva_pagos >= poliza.get("total_pagos", 0):
        update["$set"]["estado"] = "completada"

    await db.pagos.insert_one(pago)
    await db.polizas.update_one({"id": poliza_id}, update)
    poliza_actualizada = await db.polizas.find_one({"id": poliza_id})

    return poliza_actualizada, f"Pago mensual #{poliza_actualizada.get('pagos_realizados', 0)} procesado exitosamente"


async def obtener_proximos_pagos_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> List[dict]:
    limite = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    cursor = db.polizas.find({
        "usuario_id": usuario_id,
        "estado": "activa",
        "proximo_pago": {"$lte": limite}
    })
    return [doc async for doc in cursor]


async def crear_usuario(db: AsyncIOMotorDatabase, usuario: schemas.UsuarioCreate) -> dict:
    data = usuario.model_dump()
    data.setdefault("id", str(uuid.uuid4()))
    data.setdefault("saldo", 0.0)
    data.setdefault("activo", True)
    data.setdefault("fecha_registro", datetime.datetime.utcnow())
    await db.usuarios.insert_one(data)
    return data


async def obtener_usuario(db: AsyncIOMotorDatabase, usuario_id: str) -> Optional[dict]:
    return await db.usuarios.find_one({"id": usuario_id})
