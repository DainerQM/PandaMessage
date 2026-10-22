# PandaMessage

Cliente GUI para envío masivo de mensajes vía UltraMsg (interfaz PyQt6).

Características principales:
- Interfaz con tema (dark/light) y barra de título personalizada.
- Panel de bienvenida para configurar número, ID y token (guardado en `config.json`).
- Carga de números desde archivos `.txt` (botón "Cargar .txt" o arrastrar y soltar).
- Registro de actividad (historial) almacenado en la carpeta `database/`.
- Integración con la API de UltraMsg (cliente en `core/ultramsg.py`).

Estructura relevante:
- `main.py` — punto de entrada de la aplicación.
- `ui/main_window.py` — interfaz principal y lógica de UI.
- `core/ultramsg.py` — cliente HTTP para UltraMsg.
- `themes/` — archivos de tema JSON.
- `assets/` — iconos y recursos.
- `database/history.txt` — historial de envíos y eventos.
- `config.json` — configuración guardada por el panel de bienvenida.

Cómo ejecutar

1. Crear un entorno virtual (recomendado):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecutar la app desde la carpeta del proyecto:

```powershell
python main.py
```

Notas
- Asegúrate de completar el panel de bienvenida con el número (en formato internacional), el ID y el Token de UltraMsg.
- Los números pueden cargarse desde archivos `.txt` (un número por línea). La aplicación normaliza los números al enviar.
- El historial se guarda en `database/history.txt`.

Empaquetado (Windows .exe + instalador)

1) Instala dependencias y PyInstaller en tu entorno:

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

2) Crear el ejecutable (usa el script PowerShell incluido):

```powershell
.\build\build_exe.ps1 -Entry main.py -DistName PandaMessage -Icon assets\icon.ico
```

3) Generar instalador (opcional):
- Instala Inno Setup (https://jrsoftware.org/isinfo.php).
- Edita `build\panda_installer.iss`, reemplaza `{#SourceExe}` por la ruta al exe en `dist\`.
- Compila el script con Inno Setup para obtener un instalador .exe.

Licencia
- Proyecto personal. Modifica según tus necesidades.
