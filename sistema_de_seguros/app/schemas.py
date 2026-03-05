from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Usuarios
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: str
    saldo: float
    fecha_registro: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# Seguros
class SeguroBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    duracion_meses: int
    precio: float
    cuota_mensual: float
    cobertura: float
    tipo: str
    beneficios: Optional[str] = None

class SeguroCreate(SeguroBase):
    pass

class Seguro(SeguroBase):
    id: str
    activo: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

# Pólizas
class PolizaBase(BaseModel):
    usuario_id: str
    seguro_id: str

class PolizaCreate(PolizaBase):
    pass

class Poliza(PolizaBase):
    id: str
    estado: str
    fecha_compra: datetime
    fecha_vencimiento: datetime
    proximo_pago: datetime
    pagos_realizados: int
    total_pagos: int
    
    class Config:
        from_attributes = True

# Pagos
class PagoBase(BaseModel):
    poliza_id: str
    monto: float
    metodo_pago: str

class PagoCreate(PagoBase):
    pass

class Pago(PagoBase):
    id: str
    fecha_pago: datetime
    estado: str
    
    class Config:
        from_attributes = True

# Requests específicos
class DepositoRequest(BaseModel):
    monto: float

class CompraSeguroRequest(BaseModel):
    seguro_id: str

class PagoCuotaRequest(BaseModel):
    poliza_id: str
    metodo_pago: str = "saldo"

# Respuestas detalladas
class PolizaDetalle(Poliza):
    seguro: Seguro
    usuario: Usuario
    pagos: List[Pago] = []

class SeguroConBeneficios(Seguro):
    beneficios_lista: List[str] = []
    
    class Config:
        from_attributes = True