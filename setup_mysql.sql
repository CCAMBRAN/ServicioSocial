-- ============================================
-- Script de Configuración MySQL para Sistema de Seguros
-- ============================================

-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS seguros_db_sql 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Usar la base de datos
USE seguros_db_sql;

-- 3. Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    saldo DECIMAL(10, 2) DEFAULT 500.00,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Crear tabla de seguros (referencia, aunque principalmente en MongoDB)
CREATE TABLE IF NOT EXISTS seguros (
    id VARCHAR(36) PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50),
    precio DECIMAL(10, 2) NOT NULL,
    cuota_mensual DECIMAL(10, 2) NOT NULL,
    cobertura DECIMAL(12, 2) NOT NULL,
    duracion_meses INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tipo (tipo),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Crear tabla de pólizas
CREATE TABLE IF NOT EXISTS polizas (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(36) NOT NULL,
    seguro_id VARCHAR(36) NOT NULL,
    estado ENUM('activa', 'vencida', 'cancelada') DEFAULT 'activa',
    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_fin DATETIME,
    monto_total DECIMAL(10, 2) NOT NULL,
    cuota_mensual DECIMAL(10, 2) NOT NULL,
    cuotas_pagadas INT DEFAULT 0,
    cuotas_totales INT NOT NULL,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (seguro_id) REFERENCES seguros(id) ON DELETE RESTRICT,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_seguro (seguro_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_inicio (fecha_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Crear tabla de pagos
CREATE TABLE IF NOT EXISTS pagos (
    id VARCHAR(36) PRIMARY KEY,
    poliza_id VARCHAR(36) NOT NULL,
    usuario_id VARCHAR(36) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(50) DEFAULT 'saldo',
    estado ENUM('completado', 'pendiente', 'fallido') DEFAULT 'completado',
    numero_cuota INT NOT NULL,
    
    FOREIGN KEY (poliza_id) REFERENCES polizas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    
    INDEX idx_poliza (poliza_id),
    INDEX idx_usuario (usuario_id),
    INDEX idx_fecha (fecha_pago),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Crear tabla de auditoría
CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id VARCHAR(36),
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(50) NOT NULL,
    registro_id VARCHAR(36),
    datos_anteriores JSON,
    datos_nuevos JSON,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_tabla (tabla_afectada),
    INDEX idx_timestamp (timestamp),
    INDEX idx_accion (accion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Ver las tablas creadas
SHOW TABLES;

-- 9. Verificar estructura de las tablas
DESCRIBE usuarios;
DESCRIBE polizas;
DESCRIBE pagos;
DESCRIBE auditoria;
