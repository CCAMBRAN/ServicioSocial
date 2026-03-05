# 📮 Guía Completa para Testing en Postman - Sistema Híbrido

## 🔧 Configuración Inicial en Postman

### 1. Crear Nueva Colección
1. Abre Postman
2. Click en **"New Collection"**
3. Nombre: **"Sistema de Seguros - Híbrido"**
4. Guarda

### 2. Variable de Entorno
1. Click en **"Environments"** → **"Create Environment"**
2. Nombre: **"Local Development"**
3. Agregar variables:
   - `base_url` = `http://localhost:8000`
   - `api_path` = `/api/v1`
   - `usuario_id` = (dejar vacío, se llenará después)
   - `poliza_id` = (dejar vacío)
   
4. Guardar y activar el environment

---

## 🧪 FLUJO DE PRUEBA COMPLETO

### **PASO 1: Ver Seguros Disponibles** (MongoDB)

**Endpoint**: `GET {{base_url}}{{api_path}}/seguros/`

**Headers**: Ninguno necesario

**Body**: Ninguno

**Respuesta Esperada** (200 OK):
```json
[
  {
    "id": "uuid-abc-123",
    "nombre": "Seguro Básico Familiar",
    "descripcion": "Protección esencial para tu familia a un precio accesible",
    "duracion_meses": 12,
    "precio": 50.0,
    "cuota_mensual": 25.0,
    "cobertura": 10000.0,
    "tipo": "basico",
    "beneficios": "✓ Asistencia médica básica\n✓ Apoyo en gastos funerarios\n✓ Asistencia legal básica",
    "activo": true,
    "fecha_creacion": "2024-11-30T14:00:00.000Z"
  },
  {
    "id": "uuid-def-456",
    "nombre": "Seguro Estándar Hogar",
    "tipo": "estandar",
    "precio": 100.0,
    "cuota_mensual": 45.0
  },
  {
    "id": "uuid-ghi-789",
    "nombre": "Seguro Premium Integral",
    "tipo": "premium",
    "precio": 150.0,
    "cuota_mensual": 65.0
  }
]
```

**Acción**: 
- Copia un `id` de seguro (ej: el primero)
- Guárdalo en un archivo de texto (lo necesitarás después)

---

### **PASO 2: Filtrar Seguros por Tipo** (MongoDB)

**Endpoint**: `GET {{base_url}}{{api_path}}/seguros/economicos/basico`

Opciones: `basico`, `estandar`, `premium`

**Respuesta Esperada** (200 OK):
```json
[
  {
    "id": "uuid-abc-123",
    "nombre": "Seguro Básico Familiar",
    "tipo": "basico",
    "precio": 50.0,
    "cuota_mensual": 25.0
  }
]
```

---

### **PASO 3: Crear Usuario** (MySQL) ⭐

**Endpoint**: `POST {{base_url}}{{api_path}}/usuarios/`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "telefono": "5551234567"
}
```

**Respuesta Esperada** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "telefono": "5551234567",
  "saldo": 500.0,
  "activo": true,
  "fecha_registro": "2024-11-30T14:30:00.123456"
}
```

**Acción IMPORTANTE**:
1. Copia el `id` del usuario
2. En Postman, ve a **Environments** → selecciona tu environment
3. Pega el ID en la variable `usuario_id`
4. Guarda

**Tests en Postman** (pestaña "Tests"):
```javascript
// Guardar usuario_id automáticamente
pm.test("Usuario creado exitosamente", function () {
    var jsonData = pm.response.json();
    pm.environment.set("usuario_id", jsonData.id);
    pm.expect(jsonData.saldo).to.eql(500);
});
```

---

### **PASO 4: Ver Usuario Creado** (MySQL)

**Endpoint**: `GET {{base_url}}{{api_path}}/usuarios/{{usuario_id}}`

**Respuesta Esperada** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nombre": "Juan Pérez",
  "email": "juan.perez@example.com",
  "telefono": "5551234567",
  "saldo": 500.0,
  "activo": true,
  "fecha_registro": "2024-11-30T14:30:00.123456"
}
```

---

### **PASO 5: Listar Todos los Usuarios** (MySQL)

**Endpoint**: `GET {{base_url}}{{api_path}}/usuarios/`

**Query Parameters** (opcional):
- `skip` = 0
- `limit` = 10

**Respuesta Esperada** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Juan Pérez",
    "email": "juan.perez@example.com",
    "saldo": 500.0,
    "activo": true
  }
]
```

---

### **PASO 6: Comprar un Seguro** (Híbrido: MySQL + MongoDB) ⭐⭐

**Endpoint**: `POST {{base_url}}{{api_path}}/usuarios/{{usuario_id}}/comprar-seguro`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "seguro_id": "PEGA-AQUI-EL-ID-DEL-SEGURO-DEL-PASO-1"
}
```

**Ejemplo completo**:
```json
{
  "seguro_id": "uuid-abc-123"
}
```

**Respuesta Esperada** (200 OK):
```json
{
  "mensaje": "Seguro comprado exitosamente",
  "poliza_id": "poliza-uuid-xyz-999",
  "seguro_nombre": "Seguro Básico Familiar",
  "monto_pagado": 50.0,
  "nuevo_saldo": 450.0,
  "cuota_mensual": 25.0,
  "cuotas_totales": 12
}
```

**Acción**:
- Copia el `poliza_id`
- Guárdalo en la variable de entorno `poliza_id`

**Tests**:
```javascript
pm.test("Seguro comprado", function () {
    var jsonData = pm.response.json();
    pm.environment.set("poliza_id", jsonData.poliza_id);
    pm.expect(jsonData.nuevo_saldo).to.be.below(500);
});
```

**Error Posible** (400):
```json
{
  "detail": "Saldo insuficiente. Necesitas $150, tienes $50"
}
```

---

### **PASO 7: Ver Pólizas del Usuario** (Híbrido)

**Endpoint**: `GET {{base_url}}{{api_path}}/usuarios/{{usuario_id}}/polizas`

**Respuesta Esperada** (200 OK):
```json
{
  "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_polizas": 1,
  "polizas": [
    {
      "poliza_id": "poliza-uuid-xyz-999",
      "seguro_nombre": "Seguro Básico Familiar",
      "seguro_tipo": "basico",
      "estado": "activa",
      "monto_total": 50.0,
      "cuota_mensual": 25.0,
      "cuotas_pagadas": 0,
      "cuotas_totales": 12,
      "fecha_inicio": "2024-11-30T14:35:00",
      "fecha_fin": "2025-11-30T14:35:00"
    }
  ]
}
```

---

### **PASO 8: Ver Próximos Pagos Pendientes** (Híbrido)

**Endpoint**: `GET {{base_url}}{{api_path}}/usuarios/{{usuario_id}}/proximos-pagos`

**Respuesta Esperada** (200 OK):
```json
{
  "usuario_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_polizas_activas": 1,
  "proximos_pagos": [
    {
      "poliza_id": "poliza-uuid-xyz-999",
      "seguro_nombre": "Seguro Básico Familiar",
      "seguro_tipo": "basico",
      "cuota_mensual": 25.0,
      "cuotas_pagadas": 0,
      "cuotas_totales": 12,
      "cuotas_pendientes": 12,
      "fecha_inicio": "2024-11-30T14:35:00",
      "fecha_fin": "2025-11-30T14:35:00"
    }
  ]
}
```

---

### **PASO 9: Pagar Primera Cuota** (MySQL) ⭐⭐

**Endpoint**: `POST {{base_url}}{{api_path}}/polizas/{{poliza_id}}/pagar-cuota`

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "metodo_pago": "saldo"
}
```

**Respuesta Esperada** (200 OK):
```json
{
  "mensaje": "Cuota pagada exitosamente",
  "pago_id": "pago-uuid-123",
  "numero_cuota": 1,
  "monto_pagado": 25.0,
  "nuevo_saldo": 425.0,
  "cuotas_pagadas": 1,
  "cuotas_totales": 12,
  "estado_poliza": "activa"
}
```

---

### **PASO 10: Ver Historial de Pagos de la Póliza** (MySQL)

**Endpoint**: `GET {{base_url}}{{api_path}}/polizas/{{poliza_id}}/pagos`

**Respuesta Esperada** (200 OK):
```json
{
  "poliza_id": "poliza-uuid-xyz-999",
  "total_pagos": 1,
  "pagos": [
    {
      "pago_id": "pago-uuid-123",
      "monto": 25.0,
      "fecha_pago": "2024-11-30T14:40:00",
      "numero_cuota": 1,
      "metodo_pago": "saldo",
      "estado": "completado"
    }
  ]
}
```

---

### **PASO 11: Pagar Segunda Cuota**

Repite el PASO 9 con el mismo endpoint.

**Respuesta Esperada**:
```json
{
  "mensaje": "Cuota pagada exitosamente",
  "numero_cuota": 2,
  "monto_pagado": 25.0,
  "nuevo_saldo": 400.0,
  "cuotas_pagadas": 2,
  "cuotas_totales": 12
}
```

---

## 🔴 PRUEBAS DE ERRORES

### Error 1: Email Duplicado

**Endpoint**: `POST {{base_url}}{{api_path}}/usuarios/`

**Body**:
```json
{
  "nombre": "Otro Usuario",
  "email": "juan.perez@example.com",
  "telefono": "5559999999"
}
```

**Respuesta Esperada** (400):
```json
{
  "detail": "El email ya está registrado"
}
```

---

### Error 2: Saldo Insuficiente para Comprar Seguro

**Endpoint**: `POST {{base_url}}{{api_path}}/usuarios/{{usuario_id}}/comprar-seguro`

**Body** (intentar comprar Premium con solo $150 disponibles):
```json
{
  "seguro_id": "ID-DEL-SEGURO-PREMIUM"
}
```

**Respuesta Esperada** (400):
```json
{
  "detail": "Saldo insuficiente. Necesitas $150, tienes $100"
}
```

---

### Error 3: Saldo Insuficiente para Pagar Cuota

Después de gastar todo el saldo:

**Endpoint**: `POST {{base_url}}{{api_path}}/polizas/{{poliza_id}}/pagar-cuota`

**Respuesta Esperada** (400):
```json
{
  "detail": "Saldo insuficiente. Necesitas $25, tienes $0"
}
```

---

### Error 4: Usuario No Encontrado

**Endpoint**: `GET {{base_url}}{{api_path}}/usuarios/id-falso-123`

**Respuesta Esperada** (404):
```json
{
  "detail": "Usuario no encontrado"
}
```

---

### Error 5: Seguro No Encontrado

**Endpoint**: `POST {{base_url}}{{api_path}}/usuarios/{{usuario_id}}/comprar-seguro`

**Body**:
```json
{
  "seguro_id": "seguro-inexistente-999"
}
```

**Respuesta Esperada** (404):
```json
{
  "detail": "Seguro no encontrado"
}
```

---

## 📊 CREAR MÚLTIPLES USUARIOS PARA PRUEBAS

### Usuario 1: Juan (Básico)
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@test.com",
  "telefono": "5551111111"
}
```

### Usuario 2: María (Estándar)
```json
{
  "nombre": "María García",
  "email": "maria@test.com",
  "telefono": "5552222222"
}
```

### Usuario 3: Carlos (Premium)
```json
{
  "nombre": "Carlos López",
  "email": "carlos@test.com",
  "telefono": "5553333333"
}
```

### Usuario 4: Ana (Sin saldo suficiente)
```json
{
  "nombre": "Ana Martínez",
  "email": "ana@test.com",
  "telefono": "5554444444"
}
```

---

## 🎯 ESCENARIOS DE PRUEBA COMPLETOS

### **Escenario A: Usuario Compra y Paga Todas las Cuotas**

1. Crear usuario con saldo $500
2. Comprar seguro básico ($50) → saldo $450
3. Pagar cuota 1 ($25) → saldo $425
4. Pagar cuota 2 ($25) → saldo $400
5. ... repetir hasta 12 cuotas
6. Verificar que póliza quede como "vencida"

---

### **Escenario B: Usuario Compra Múltiples Seguros**

1. Crear usuario con saldo $500
2. Comprar seguro básico ($50) → saldo $450
3. Comprar seguro estándar ($100) → saldo $350
4. Ver pólizas activas (debería mostrar 2)
5. Ver próximos pagos (debería mostrar 2 cuotas pendientes)

---

### **Escenario C: Verificar Auditoría** (MySQL directo)

Después de crear usuarios y hacer compras, abre **phpMyAdmin**:

```sql
-- Ver auditoría de usuario
SELECT * FROM auditoria 
WHERE usuario_id = 'TU-USUARIO-ID'
ORDER BY timestamp DESC;

-- Ver todas las acciones
SELECT accion, tabla_afectada, timestamp 
FROM auditoria 
ORDER BY timestamp DESC 
LIMIT 10;
```

---

## 📝 COLLECTION DE POSTMAN - PRE-REQUEST SCRIPT

Para automatizar todo el flujo, agrega esto en la pestaña **"Pre-request Script"** de la colección:

```javascript
// Generar email único para cada prueba
const timestamp = Date.now();
pm.environment.set("unique_email", `test${timestamp}@example.com`);
```

Luego en el body de crear usuario:
```json
{
  "nombre": "Test User",
  "email": "{{unique_email}}",
  "telefono": "5555555555"
}
```

---

## 🔗 ORDEN RECOMENDADO DE PRUEBAS

1. ✅ `GET /seguros/` - Ver catálogo
2. ✅ `GET /seguros/economicos/basico` - Filtrar
3. ✅ `POST /usuarios/` - Crear usuario
4. ✅ `GET /usuarios/{{usuario_id}}` - Verificar usuario
5. ✅ `POST /usuarios/{id}/comprar-seguro` - Comprar
6. ✅ `GET /usuarios/{id}/polizas` - Ver pólizas
7. ✅ `GET /usuarios/{id}/proximos-pagos` - Ver pagos pendientes
8. ✅ `POST /polizas/{id}/pagar-cuota` - Pagar cuota
9. ✅ `GET /polizas/{id}/pagos` - Ver historial
10. ✅ Repetir pasos 8-9 para más cuotas

---

## 🎨 ORGANIZACIÓN EN POSTMAN

**Carpetas sugeridas**:

```
📁 Sistema de Seguros - Híbrido
  ├─ 📂 1. Seguros (MongoDB)
  │   ├─ GET Listar Seguros
  │   ├─ GET Filtrar por Tipo
  │   └─ POST Crear Seguro
  │
  ├─ 📂 2. Usuarios (MySQL)
  │   ├─ GET Listar Usuarios
  │   ├─ POST Crear Usuario
  │   └─ GET Ver Usuario
  │
  ├─ 📂 3. Compras (Híbrido)
  │   ├─ POST Comprar Seguro
  │   ├─ GET Ver Pólizas
  │   └─ GET Próximos Pagos
  │
  ├─ 📂 4. Pagos (MySQL)
  │   ├─ POST Pagar Cuota
  │   └─ GET Historial Pagos
  │
  └─ 📂 5. Pruebas de Errores
      ├─ Email Duplicado
      ├─ Saldo Insuficiente
      └─ Usuario No Encontrado
```

---

¡Listo! Con esta guía puedes probar todo el sistema híbrido paso a paso. 🚀
