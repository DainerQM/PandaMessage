# PandaMessage

Aplicaci?n de escritorio para preparar y enviar mensajes de texto de WhatsApp a varios destinatarios usando una instancia activa de [UltraMsg](https://ultramsg.com/). Est? construida con Python y PyQt6.

La aplicaci?n ofrece una interfaz en espa?ol, temas claro y oscuro, importaci?n de n?meros desde archivos de texto, resultados de env?o e historial exportable.

> **Antes de enviar:** revisa el mensaje y cada n?mero. Env?a ?nicamente a personas que hayan aceptado recibirlo y cumple las condiciones de WhatsApp y UltraMsg. Los mensajes enviados no se pueden retirar desde PandaMessage. La aplicaci?n procesa los destinatarios de forma secuencial y no configura pausas entre solicitudes.

## Contenido

- [Funciones](#funciones)
- [Requisitos](#requisitos)
- [Instalar y ejecutar desde el c?digo](#instalar-y-ejecutar-desde-el-c?digo)
- [Configurar UltraMsg](#configurar-ultramsg)
- [Enviar mensajes](#enviar-mensajes)
- [Configuraci?n e historial](#configuraci?n-e-historial)
- [Crear el ejecutable y el instalador de Windows](#crear-el-ejecutable-y-el-instalador-de-windows)
- [Soluci?n de problemas](#soluci?n-de-problemas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Tecnolog?as y licencia](#tecnolog?as-y-licencia)

## Funciones

- Interfaz gr?fica en espa?ol con temas claro y oscuro.
- Configuraci?n del n?mero remitente, el ID de instancia y el token de UltraMsg desde la aplicaci?n.
- Composici?n de mensajes de texto, incluidos emojis.
- Ingreso de destinatarios, uno por l?nea, o importaci?n desde un archivo `.txt`.
- Compatibilidad con arrastrar y soltar archivos `.txt` en el ?rea de destinatarios.
- Eliminaci?n de espacios, signos y otros caracteres que no sean d?gitos en los n?meros.
- Env?o en segundo plano para mantener la ventana interactiva; los destinatarios se procesan uno por uno.
- Estado visible de los env?os e historial de actividad que puede exportarse a un archivo de texto.

La interfaz permite enviar texto. Aunque el m?dulo de API contiene una funci?n de env?o de medios, esa funci?n no est? disponible como acci?n en la interfaz.

## Requisitos

- **Para el instalador:** Windows 10 o posterior.
- **Para ejecutar desde el c?digo:** Python 3 y `pip`, en un entorno compatible con PyQt6.
- Una cuenta de UltraMsg con una instancia activa, su ID y un token v?lido.
- Conexi?n a Internet para comunicarse con la API de UltraMsg.

El proyecto no requiere paquetes adicionales fuera de los declarados en `requirements.txt`.

## Instalar y ejecutar desde el c?digo

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

En otros sistemas, la activaci?n del entorno virtual puede variar. Por ejemplo, en macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Configurar UltraMsg

En el primer inicio, completa los datos solicitados en la ventana de bienvenida o abre **Configuraci?n**:

1. **N?mero de tel?fono:** n?mero remitente en formato internacional, incluido el c?digo de pa?s.
2. **ID:** ID de la instancia de UltraMsg.
3. **Token:** token de API de esa instancia.

Guarda la configuraci?n antes de enviar. Debes tener una instancia de UltraMsg activa y vinculada al n?mero remitente.

## Enviar mensajes

1. Escribe el mensaje en el ?rea de texto.
2. Introduce los n?meros destinatarios, **uno por l?nea**, o pulsa **Cargar .txt** para seleccionar un archivo de texto. Tambi?n puedes arrastrar y soltar un `.txt` en el ?rea de n?meros.
3. Revisa el mensaje y la lista completa antes de continuar.
4. Pulsa **Enviar ahora** y consulta los resultados en el panel de actividad.

Ejemplo de archivo `.txt`:

```text
+1 202 555 0142
+44 20 7946 0958
+57 300 123 4567
```

PandaMessage elimina los caracteres que no sean d?gitos; por ejemplo, `+57 300 123 4567` se convierte en `573001234567`. Esta limpieza **no valida** que el n?mero exista ni agrega un c?digo de pa?s que falte. Comprueba que cada destinatario tenga el prefijo internacional correcto. El selector de archivos admite `.txt`; no convierte hojas de c?lculo ni interpreta columnas CSV.

Los mensajes se env?an en secuencia a trav?s de UltraMsg. El panel muestra el resultado comunicado por la API para cada destinatario y registra la actividad en el historial.

## Configuraci?n e historial

La configuraci?n se guarda como `config.json` en una carpeta del usuario:

- Windows: `%LOCALAPPDATA%\PandaMessage\config.json`
- macOS y Linux: `~/.pandamessage/config.json`

El token se guarda en texto legible en ese archivo; PandaMessage no lo cifra. No compartas ni subas el archivo de configuraci?n. Protege tu cuenta y token de UltraMsg como credenciales privadas.

Al ejecutar desde el c?digo fuente, el historial est? en `database/history.txt`. Puedes abrirlo desde **Historial** y usar **Exportar** para guardar una copia en otra ubicaci?n.

En el instalador de Windows, la aplicaci?n resuelve la carpeta del historial dentro de los recursos empaquetados. Esa ubicaci?n puede estar protegida contra escritura por Windows; exporta el historial a una carpeta de usuario y verifica que se haya guardado correctamente.

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

El instalador configura la instalaci?n en `Program Files` y requiere privilegios de administrador. El repositorio actualmente no tiene una versi?n publicada en la p?gina de Releases; puedes construir el instalador siguiendo estos pasos.

## Soluci?n de problemas

- **No abre la ventana o aparece `ModuleNotFoundError`:** activa el entorno virtual y ejecuta `python -m pip install -r requirements.txt` usando el mismo int?rprete con el que ejecutas `main.py`.
- **Faltan credenciales o la API rechaza el env?o:** verifica el ID de instancia, el token, que la instancia est? activa y que el n?mero remitente configurado sea el correcto.
- **El destinatario no recibe el mensaje:** comprueba el c?digo de pa?s y el n?mero, la conexi?n a Internet y el estado de la instancia en UltraMsg. Revisa tambi?n las condiciones y l?mites vigentes del servicio.
- **No se encuentra el historial:** al ejecutar desde el c?digo, revisa `database/history.txt`. Desde la ventana de historial, exporta una copia a una carpeta donde tengas permiso de escritura.

## Estructura del proyecto

```text
PandaMessage/
??? assets/                 # Iconos de la aplicaci?n
??? core/                   # Cliente para la API de UltraMsg
??? themes/                 # Definiciones de temas claro y oscuro
??? ui/                     # Ventana y componentes PyQt6
??? database/               # Historial generado al ejecutar desde el c?digo
??? main.py                 # Punto de entrada de la aplicaci?n
??? requirements.txt        # Dependencias de Python
??? PandaMessage.spec       # Configuraci?n de PyInstaller
??? PandaMessage_Setup.iss  # Script del instalador de Inno Setup
```

## Tecnolog?as y licencia

- Python 3
- PyQt6
- Requests
- [UltraMsg API](https://ultramsg.com/)
- PyInstaller e Inno Setup para crear la distribuci?n de Windows

El repositorio no incluye un archivo de licencia. Consulta al propietario antes de redistribuir o reutilizar el c?digo.
