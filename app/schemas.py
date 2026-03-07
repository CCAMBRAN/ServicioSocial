from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime


# Usuarios

class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    tipo_usuario: Literal["fondeador", "beneficiario"] 

class Usuario(UsuarioBase):
    id: str
    tipo_usuario: Literal["fondeador", "beneficiario"]
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
    beneficiario_id: str
    seguro_id: str

class PolizaCreate(PolizaBase):
    fondeador_id: Optional[str] = None

class Poliza(PolizaBase):
    id: str
    fondeador_id: Optional[str] = None
    estado: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    monto_total: float
    cuota_mensual: float
    cuotas_pagadas: int
    cuotas_totales: int
    
    class Config:
        from_attributes = True

# Pagos
class PagoBase(BaseModel):
    poliza_id: str
    usuario_id: str
    monto: float

class PagoCreate(BaseModel):
    numero_cuota: int
    tipo_pago: str = "cuota_mensual"

class Pago(PagoBase):
    id: str
    fecha_pago: datetime
    numero_cuota: int
    tipo_pago: str
    estado: str
    metodo_pago: str
    
    class Config:
        from_attributes = True

# Requests específicos
class DepositoRequest(BaseModel):
    monto: float

class CompraSeguroRequest(BaseModel):
    seguro_id: str
    fondeador_id: Optional[str] = None

class PagoCuotaRequest(BaseModel):
    poliza_id: str
    metodo_pago: str = "saldo"
    usuario_pagador_id: Optional[str] = None

# Respuestas detalladas
class PolizaDetalle(Poliza):
    seguro: Seguro
    usuario: Usuario
    pagos: List[Pago] = []

class SeguroConBeneficios(Seguro):
    beneficios_lista: List[str] = []
    
    class Config:
        from_attributes = True