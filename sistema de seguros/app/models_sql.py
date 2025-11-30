"""
Modelos SQLAlchemy para MySQL
Define las tablas y relaciones del sistema de seguros
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database_sql import Base
import enum


# Enums para campos con valores específicos
class EstadoPoliza(str, enum.Enum):
    ACTIVA = "activa"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


class EstadoPago(str, enum.Enum):
    COMPLETADO = "completado"
    PENDIENTE = "pendiente"
    FALLIDO = "fallido"


# ============================================
# Modelo: Usuario
# ============================================
class UsuarioSQL(Base):
    __tablename__ = "usuarios"
    
    id = Column(String(36), primary_key=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20))
    saldo = Column(Numeric(10, 2), default=500.00)
    activo = Column(Boolean, default=True, index=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    
    # Relaciones
    polizas = relationship("PolizaSQL", back_populates="usuario", cascade="all, delete-orphan")
    pagos = relationship("PagoSQL", back_populates="usuario", cascade="all, delete-orphan")
    auditorias = relationship("AuditoriaSQL", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre}, email={self.email})>"


# ============================================
# Modelo: Seguro
# ============================================
class SeguroSQL(Base):
    __tablename__ = "seguros"
    
    id = Column(String(36), primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(50), index=True)
    precio = Column(Numeric(10, 2), nullable=False)
    cuota_mensual = Column(Numeric(10, 2), nullable=False)
    cobertura = Column(Numeric(12, 2), nullable=False)
    duracion_meses = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
    
    # Relaciones
    polizas = relationship("PolizaSQL", back_populates="seguro")
    
    def __repr__(self):
        return f"<Seguro(id={self.id}, nombre={self.nombre}, tipo={self.tipo})>"


# ============================================
# Modelo: Póliza
# ============================================
class PolizaSQL(Base):
    __tablename__ = "polizas"
    
    id = Column(String(36), primary_key=True)
    usuario_id = Column(String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    seguro_id = Column(String(36), ForeignKey("seguros.id", ondelete="RESTRICT"), nullable=False, index=True)
    estado = Column(SQLEnum(EstadoPoliza), default=EstadoPoliza.ACTIVA, index=True)
    fecha_inicio = Column(DateTime, server_default=func.now(), index=True)
    fecha_fin = Column(DateTime)
    monto_total = Column(Numeric(10, 2), nullable=False)
    cuota_mensual = Column(Numeric(10, 2), nullable=False)
    cuotas_pagadas = Column(Integer, default=0)
    cuotas_totales = Column(Integer, nullable=False)
    
    # Relaciones
    usuario = relationship("UsuarioSQL", back_populates="polizas")
    seguro = relationship("SeguroSQL", back_populates="polizas")
    pagos = relationship("PagoSQL", back_populates="poliza", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Poliza(id={self.id}, usuario_id={self.usuario_id}, estado={self.estado})>"


# ============================================
# Modelo: Pago
# ============================================
class PagoSQL(Base):
    __tablename__ = "pagos"
    
    id = Column(String(36), primary_key=True)
    poliza_id = Column(String(36), ForeignKey("polizas.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(String(36), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(DateTime, server_default=func.now(), index=True)
    metodo_pago = Column(String(50), default="saldo")
    estado = Column(SQLEnum(EstadoPago), default=EstadoPago.COMPLETADO, index=True)
    numero_cuota = Column(Integer, nullable=False)
    
    # Relaciones
    poliza = relationship("PolizaSQL", back_populates="pagos")
    usuario = relationship("UsuarioSQL", back_populates="pagos")
    
    def __repr__(self):
        return f"<Pago(id={self.id}, poliza_id={self.poliza_id}, monto={self.monto})>"


# ============================================
# Modelo: Auditoría
# ============================================
class AuditoriaSQL(Base):
    __tablename__ = "auditoria"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(String(36), ForeignKey("usuarios.id", ondelete="SET NULL"), index=True)
    accion = Column(String(100), nullable=False, index=True)
    tabla_afectada = Column(String(50), nullable=False, index=True)
    registro_id = Column(String(36))
    datos_anteriores = Column(JSON)
    datos_nuevos = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    
    # Relaciones
    usuario = relationship("UsuarioSQL", back_populates="auditorias")
    
    def __repr__(self):
        return f"<Auditoria(id={self.id}, accion={self.accion}, tabla={self.tabla_afectada})>"
