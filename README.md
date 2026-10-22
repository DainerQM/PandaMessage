# PandaMessage

Cliente de escritorio para preparar y enviar mensajes de WhatsApp a una lista de destinatarios mediante la API de [UltraMsg](https://ultramsg.com/).

PandaMessage está desarrollado con Python y PyQt6. La interfaz permite preparar el mensaje y la lista de números, revisar el estado de los envíos y consultar el historial de actividad.

## Funciones

- Interfaz gráfica en español con temas claro y oscuro.
- Configuración de número remitente, ID de instancia y token de UltraMsg desde la aplicación.
- Importación de destinatarios desde archivos `.txt` o arrastrando el archivo a la lista.
- Normalización de números: elimina espacios, signos y caracteres que no sean dígitos.
- Envío en segundo plano para mantener la interfaz interactiva.
- Estado de cada envío e historial de actividad exportable.

> El envío requiere una instancia activa y credenciales válidas de UltraMsg. Asegúrate de tener autorización para contactar a los destinatarios y de cumplir las condiciones de uso de WhatsApp y UltraMsg.

## Requisitos

- Windows 10 o posterior para el instalador incluido.
- Python 3 y `pip` para ejecutar desde el código fuente.
- Una cuenta e instancia de UltraMsg con su ID y token de API.

## Instalación y ejecución

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

En el primer inicio, completa el número remitente en formato internacional, el ID de instancia y el token de UltraMsg. También puedes cambiar estos datos después desde **Configuración**.

## Enviar mensajes

1. Escribe o pega el mensaje.
2. Añade los números de destino, uno por línea, o selecciona **Cargar .txt** para importarlos.
3. Revisa el contenido y la lista de destinatarios.
4. Selecciona **Enviar ahora** y sigue el resultado en el panel de actividad.

Los números se envían secuencialmente. El panel de actividad registra los resultados y se puede abrir desde **Historial**.

## Configuración e historial

La configuración se guarda localmente en una carpeta del usuario:

- Windows: `%LOCALAPPDATA%\PandaMessage\config.json`
- Linux/macOS: `~/.pandamessage/config.json`

Al ejecutar desde el código fuente, el historial se guarda en `database/history.txt`. Usa la opción de exportación de **Historial** para guardar una copia en otra ubicación. La configuración contiene el token de UltraMsg; no compartas ese archivo ni lo publiques en GitHub.

## Crear el ejecutable de Windows

Con las dependencias instaladas, genera la aplicación con PyInstaller:

```powershell
pyinstaller --noconfirm PandaMessage.spec
```

La carpeta generada es `dist\PandaMessage\`. Para crear el instalador:

1. Instala [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Abre `PandaMessage_Setup.iss` en Inno Setup Compiler.
3. Compila el script. El instalador se genera en `installer\`.

## Estructura del proyecto

```text
PandaMessage/
├── assets/                 # Iconos de la aplicación
├── core/                   # Cliente de la API de UltraMsg
├── database/               # Historial local de actividad
├── themes/                 # Temas claro y oscuro
├── ui/                     # Interfaz PyQt6
├── main.py                 # Punto de entrada
├── PandaMessage.spec       # Configuración de PyInstaller
└── PandaMessage_Setup.iss  # Script del instalador de Inno Setup
```

## Tecnologías

- Python
- PyQt6
- Requests
- UltraMsg API

## Licencia

No se ha especificado una licencia. Todos los derechos permanecen reservados a sus respectivos titulares mientras no se añada una licencia al repositorio.
