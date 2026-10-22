# 📦 INSTALADOR PROFESIONAL - PandaMessage

## 🎯 ¿Qué hace este instalador?

El instalador **PandaMessage_Setup.iss** crea un instalador profesional que:

✅ **Instala en Program Files** - Como cualquier programa profesional  
✅ **Crea accesos directos** - Escritorio y menú inicio  
✅ **Registra en el sistema** - Aparece en "Programas y características"  
✅ **Desinstalador automático** - Limpieza completa del sistema  
✅ **Interfaz moderna** - Wizard profesional con tu icono  
✅ **Multiidioma** - Español e inglés  
✅ **Detección de versiones** - Actualiza instalaciones previas  

---

## 🚀 PASOS PARA CREAR EL INSTALADOR:

### 1️⃣ **Descargar Inno Setup**
- Ve a: https://jrsoftware.org/isdl.php
- Descarga **Inno Setup 6.x** (GRATIS)
- Instálalo normalmente

### 2️⃣ **Abrir el script**
- Abre **Inno Setup Compiler**
- Archivo → Abrir → Selecciona `PandaMessage_Setup.iss`

### 3️⃣ **Compilar el instalador**
- Menú **Build** → **Compile**
- ¡Listo! Se creará `installer/PandaMessage_Setup_v1.0.0.exe`

---

## 📂 RESULTADO FINAL:

```
📁 PandaMessage/
├── 📁 installer/
│   └── 🚀 PandaMessage_Setup_v1.0.0.exe  ← ¡TU INSTALADOR!
├── 📁 dist/
│   └── 📁 PandaMessage/  (archivos fuente)
└── 📄 PandaMessage_Setup.iss  (script)
```

---

## ⭐ CARACTERÍSTICAS DEL INSTALADOR:

### 🎨 **Interfaz Profesional**
- Wizard moderno de Windows
- Tu icono personalizado
- Textos en español
- Progreso visual

### 📍 **Instalación Estándar**
- Se instala en: `C:\Program Files\PandaMessage\`
- Crea acceso directo en escritorio (opcional)
- Añade al menú inicio
- Registra en el sistema

### 🔄 **Características Avanzadas**
- Detecta y actualiza versiones previas
- Desinstalador completo
- Limpieza de archivos temporales
- Opción de ejecutar después de instalar

### 🛡️ **Seguridad**
- Requiere permisos de administrador
- UUID único para evitar conflictos
- Verificación de integridad

---

## 🎯 DISTRIBUCIÓN:

Una vez compilado, `PandaMessage_Setup_v1.0.0.exe` es tu instalador final:
- ✅ **Autocontenido** - No necesita archivos adicionales
- ✅ **Portátil** - Funciona en cualquier PC Windows
- ✅ **Profesional** - Como cualquier software comercial
- ✅ **Firmable** - Puedes añadir firma digital (opcional)

---

## 🔧 PERSONALIZACIÓN (OPCIONAL):

En `PandaMessage_Setup.iss` puedes cambiar:
- **AppPublisher**: Tu nombre/empresa
- **AppVersion**: Número de versión
- **OutputBaseFilename**: Nombre del instalador final
- **DefaultDirName**: Carpeta de instalación por defecto

¡Tu aplicación ahora tiene instalador profesional! 🎉
