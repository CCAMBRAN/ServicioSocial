# 🚀 Guía de Inicio Rápido - Sistema de Seguros

## Pasos para Iniciar la Aplicación

### 1️⃣ Verificar que MongoDB esté corriendo

Abre una terminal y ejecuta:
```bash
mongod
```

O si usas MongoDB como servicio, verifica que esté activo.

### 2️⃣ Activar el entorno virtual (si usas uno)

En PowerShell:
```powershell
cd "c:\Users\alber\OneDrive\Proyectos personales\Servivio Social\sistema de seguros"
```

El entorno virtual ya está configurado automáticamente.

### 3️⃣ Iniciar el servidor FastAPI

En PowerShell, ejecuta:
```powershell
python main.py
```

O usando el intérprete de Python del entorno virtual:
```powershell
C:/Users/alber/.virtualenvs/Servivio_Social-L3sWhYvk/Scripts/python.exe main.py
```

Deberías ver algo como:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Conectado a MongoDB
✅ Paquetes de seguros económicos creados automáticamente
INFO:     Application startup complete.
```

### 4️⃣ Abrir el Frontend

Una vez que el servidor esté corriendo, abre tu navegador en:

```
http://localhost:8000
```

O también puedes usar:
```
http://127.0.0.1:8000
```

## 🌐 Explorar el Frontend

Tu sitio web tiene 4 secciones principales:

### **Inicio** 
- Página de bienvenida con información del sistema

### **Nuestros Seguros**
- Ver todos los seguros disponibles
- 3 planes: Básico ($50), Estándar ($100), Premium ($150)
- Información de cobertura, cuota mensual y beneficios

### **Registro**
- Crear tu cuenta de usuario
- Campos: Nombre, Email, Teléfono

### **Dashboard**
- Ver tu perfil (nombre, email, saldo, teléfono)
- Solo accesible después de registrarte

## 📝 Prueba Rápida

1. **Ver Seguros**:
   - Haz clic en "Nuestros Seguros"
   - Deberías ver 3 tarjetas con los planes disponibles

2. **Registrarte**:
   - Haz clic en "Registro"
   - Completa el formulario:
     - Nombre: Tu nombre
     - Email: tu@email.com
     - Teléfono: 1234567890
   - Haz clic en "Registrarse"
   - Verás un mensaje de éxito

3. **Ver Dashboard**:
   - Después de registrarte, haz clic en "Dashboard"
   - Verás tus datos guardados

4. **Comprar Seguro**:
   - Ve a "Nuestros Seguros"
   - Haz clic en "Comprar Ahora" en cualquier plan
   - Verás un mensaje de confirmación

## 🛑 Detener el Servidor

Para detener el servidor, presiona:
```
CTRL + C
```

## ⚠️ Solución de Problemas

### El servidor no inicia
- Verifica que MongoDB esté corriendo
- Asegúrate de estar en el directorio correcto
- Revisa que las dependencias estén instaladas

### El frontend no se ve
- Confirma que el servidor esté corriendo en `http://localhost:8000`
- Abre la consola del navegador (F12) para ver errores
- Verifica que el archivo `frontend/index.html` exista

### Error de CORS
- El CORS ya está configurado en `main.py`
- Si persiste, reinicia el servidor

### Los seguros no cargan
- Abre F12 → Console en el navegador
- Verifica que MongoDB esté corriendo
- Revisa que los seguros se hayan creado (verás el mensaje en la terminal)

## 📚 Archivos Importantes

- `main.py` - Servidor principal
- `frontend/index.html` - Página principal
- `frontend/css/styles.css` - Estilos
- `frontend/js/app.js` - Lógica de la aplicación
- `frontend/js/api.js` - Cliente API

## 🔗 URLs Útiles

- **Frontend**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/api/v1

---

**¡Listo!** Tu aplicación está corriendo. Explora las secciones y prueba la funcionalidad.
