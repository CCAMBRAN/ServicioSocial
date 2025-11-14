from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

class UsuarioBase(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    saldo: float = 0.0
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan@ejemplo.com",
                "telefono": "1234567890"
            }
        }

class SeguroBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    duracion_meses: int
    precio: float
    cuota_mensual: float
    cobertura: float
    tipo: str = "basico"
    beneficios: Optional[str] = None
    activo: bool = True

class SeguroCreate(SeguroBase):
    pass

class Seguro(SeguroBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

class PolizaBase(BaseModel):
    usuario_id: str
    seguro_id: str
    estado: str = "activa"
    fecha_vencimiento: datetime
    proximo_pago: datetime
    pagos_realizados: int = 0
    total_pagos: int

class PolizaCreate(PolizaBase):
    pass

class Poliza(PolizaBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fecha_compra: datetime = Field(default_factory=datetime.utcnow)

class PagoBase(BaseModel):
    poliza_id: str
    monto: float
    metodo_pago: str = "saldo"
    estado: str = "completado"

class PagoCreate(PagoBase):
    pass

class Pago(PagoBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    fecha_pago: datetime = Field(default_factory=datetime.utcnow)