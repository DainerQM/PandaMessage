# PandaMessage

Aplicación de escritorio para preparar y enviar mensajes de texto de WhatsApp a varios destinatarios usando una instancia activa de [UltraMsg](https://ultramsg.com/). Está construida con Python y PyQt6.

La aplicación ofrece una interfaz en español, temas claro y oscuro, importación de números desde archivos de texto, resultados de envío e historial exportable.

> **Antes de enviar:** revisa el mensaje y cada número. Envía únicamente a personas que hayan aceptado recibirlo y cumple las condiciones de WhatsApp y UltraMsg. Los mensajes enviados no se pueden retirar desde PandaMessage. La aplicación procesa los destinatarios de forma secuencial y no configura pausas entre solicitudes.

## Contenido

- [Funciones](#funciones)
- [Requisitos](#requisitos)
- [Instalar y ejecutar desde el código](#instalar-y-ejecutar-desde-el-código)
- [Configurar UltraMsg](#configurar-ultramsg)
- [Enviar mensajes](#enviar-mensajes)
- [Configuración e historial](#configuración-e-historial)
- [Crear el ejecutable y el instalador de Windows](#crear-el-ejecutable-y-el-instalador-de-windows)
- [Solución de problemas](#solución-de-problemas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Tecnologías y licencia](#tecnologías-y-licencia)

## Funciones

- Interfaz gráfica en español con temas claro y oscuro.
- Configuración del número remitente, el ID de instancia y el token de UltraMsg desde la aplicación.
- Composición de mensajes de texto, incluidos emojis.
- Ingreso de destinatarios, uno por línea, o importación desde un archivo `.txt`.
- Compatibilidad con arrastrar y soltar archivos `.txt` en el área de destinatarios.
- Eliminación de espacios, signos y otros caracteres que no sean dígitos en los números.
- Envío en segundo plano para mantener la ventana interactiva; los destinatarios se procesan uno por uno.
- Estado visible de los envíos e historial de actividad que puede exportarse a un archivo de texto.

La interfaz permite enviar texto. Aunque el módulo de API contiene una función de envío de medios, esa función no está disponible como acción en la interfaz.

## Requisitos

- **Para el instalador:** Windows 10 o posterior.
- **Para ejecutar desde el código:** Python 3 y `pip`, en un entorno compatible con PyQt6.
- Una cuenta de UltraMsg con una instancia activa, su ID y un token válido.
- Conexión a Internet para comunicarse con la API de UltraMsg.

El proyecto no requiere paquetes adicionales fuera de los declarados en `requirements.txt`.

## Instalar y ejecutar desde el código

En Windows, abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Si PowerShell no permite activar el entorno virtual, puedes invocar Python directamente dentro del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

En otros sistemas, la activación del entorno virtual puede variar. Por ejemplo, en macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Configurar UltraMsg

En el primer inicio, completa los datos solicitados en la ventana de bienvenida o abre **Configuración**:

1. **Número de teléfono:** número remitente en formato internacional, incluido el código de país.
2. **ID:** ID de la instancia de UltraMsg.
3. **Token:** token de API de esa instancia.

Guarda la configuración antes de enviar. Debes tener una instancia de UltraMsg activa y vinculada al número remitente.

## Enviar mensajes

1. Escribe el mensaje en el área de texto.
2. Introduce los números destinatarios, **uno por línea**, o pulsa **Cargar .txt** para seleccionar un archivo de texto. También puedes arrastrar y soltar un `.txt` en el área de números.
3. Revisa el mensaje y la lista completa antes de continuar.
4. Pulsa **Enviar ahora** y consulta los resultados en el panel de actividad.

Ejemplo de archivo `.txt`:

```text
+1 202 555 0142
+44 20 7946 0958
+57 300 123 4567
```

PandaMessage elimina los caracteres que no sean dígitos; por ejemplo, `+57 300 123 4567` se convierte en `573001234567`. Esta limpieza **no valida** que el número exista ni agrega un código de país que falte. Comprueba que cada destinatario tenga el prefijo internacional correcto. El selector de archivos admite `.txt`; no convierte hojas de cálculo ni interpreta columnas CSV.

Los mensajes se envían en secuencia a través de UltraMsg. El panel muestra el resultado comunicado por la API para cada destinatario y registra la actividad en el historial.

## Configuración e historial

La configuración se guarda como `config.json` en una carpeta del usuario:

- Windows: `%LOCALAPPDATA%\PandaMessage\config.json`
- macOS y Linux: `~/.pandamessage/config.json`

El token se guarda en texto legible en ese archivo; PandaMessage no lo cifra. No compartas ni subas el archivo de configuración. Protege tu cuenta y token de UltraMsg como credenciales privadas.

Al ejecutar desde el código fuente, el historial está en `database/history.txt`. Puedes abrirlo desde **Historial** y usar **Exportar** para guardar una copia en otra ubicación.

En el instalador de Windows, la aplicación resuelve la carpeta del historial dentro de los recursos empaquetados. Esa ubicación puede estar protegida contra escritura por Windows; exporta el historial a una carpeta de usuario y verifica que se haya guardado correctamente.

## Crear el ejecutable y el instalador de Windows

Para crear el ejecutable, primero instala las dependencias desde la carpeta del proyecto y luego ejecuta:

```powershell
python -m pip install -r requirements.txt
pyinstaller --noconfirm PandaMessage.spec
```

PyInstaller crea la carpeta `dist\PandaMessage\`. Para construir el instalador:

1. Instala [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Abre `PandaMessage_Setup.iss` con Inno Setup Compiler.
3. Selecciona **Build > Compile**. El script guarda el instalador en `installer\` con el nombre `PandaMessage_Setup_v1.0.0.exe`.

El instalador configura la instalación en `Program Files` y requiere privilegios de administrador. El repositorio actualmente no tiene una versión publicada en la página de Releases; puedes construir el instalador siguiendo estos pasos.

## Solución de problemas

- **No abre la ventana o aparece `ModuleNotFoundError`:** activa el entorno virtual y ejecuta `python -m pip install -r requirements.txt` usando el mismo intérprete con el que ejecutas `main.py`.
- **Faltan credenciales o la API rechaza el envío:** verifica el ID de instancia, el token, que la instancia esté activa y que el número remitente configurado sea el correcto.
- **El destinatario no recibe el mensaje:** comprueba el código de país y el número, la conexión a Internet y el estado de la instancia en UltraMsg. Revisa también las condiciones y límites vigentes del servicio.
- **No se encuentra el historial:** al ejecutar desde el código, revisa `database/history.txt`. Desde la ventana de historial, exporta una copia a una carpeta donde tengas permiso de escritura.

## Estructura del proyecto

```text
PandaMessage/
├── assets/                 # Iconos de la aplicación
├── core/                   # Cliente para la API de UltraMsg
├── themes/                 # Definiciones de temas claro y oscuro
├── ui/                     # Ventana y componentes PyQt6
├── database/               # Historial generado al ejecutar desde el código
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias de Python
├── PandaMessage.spec       # Configuración de PyInstaller
└── PandaMessage_Setup.iss  # Script del instalador de Inno Setup
```

## Tecnologías y licencia

- Python 3
- PyQt6
- Requests
- [UltraMsg API](https://ultramsg.com/)
- PyInstaller e Inno Setup para crear la distribución de Windows

El repositorio no incluye un archivo de licencia. Consulta al propietario antes de redistribuir o reutilizar el código.
