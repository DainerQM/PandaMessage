from PyQt6 import QtWidgets, QtGui, QtCore
import json
import os
from typing import Dict, Any
import sys


def get_user_config_path():
	"""Get the path where config.json should be stored for user write access."""
	# Use AppData/Local for Windows, which is writable by the user
	if os.name == 'nt':  # Windows
		app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
		config_dir = os.path.join(app_data, 'PandaMessage')
	else:  # Linux/Mac fallback
		config_dir = os.path.expanduser('~/.pandamessage')
	
	# Create directory if it doesn't exist
	os.makedirs(config_dir, exist_ok=True)
	return os.path.join(config_dir, 'config.json')


def resource_path(*parts):
    """Return an absolute path to resource, supporting PyInstaller _MEIPASS."""
    try:
        # When bundled by PyInstaller, resources are extracted to _MEIPASS
        base = sys._MEIPASS  # type: ignore
    except Exception:
        # Use the project root (one level above this package) as base when
        # running from source in the editor. This matches how resources are
        # laid out in the repo (assets/, themes/, database/ at project root).
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Allow callers that accidentally pass '..' (older code) to still work by
    # stripping leading '..' path fragments. Also this makes the function
    # behave the same whether running in source or inside PyInstaller's
    # _MEIPASS bundle.
    parts = [p for p in parts if p != '..']
    return os.path.abspath(os.path.join(base, *parts))


class Theme:
    def __init__(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.data = data

    def color(self, key):
        return self.data.get(key, "#000000")
    
    def display_name(self):
        """Nombre legible del tema si está presente en el JSON."""
        return self.data.get('theme_name')


def _resolve_theme_from(obj):
    """Try to find a Theme instance attached to an object (MainWindow or dialog).
    We expect dialogs to store their last applied theme in `_applied_theme` and
    MainWindow to expose `current_theme`.
    """
    if obj is None:
        return None
    if hasattr(obj, 'current_theme') and isinstance(getattr(obj, 'current_theme'), Theme):
        return getattr(obj, 'current_theme')
    if hasattr(obj, '_applied_theme') and isinstance(getattr(obj, '_applied_theme'), Theme):
        return getattr(obj, '_applied_theme')
    return None


def show_themed_message(parent, kind: str, title: str, text: str):
    """Show a QMessageBox styled to match the app theme when possible.

    kind: 'information'|'warning'|'critical'|'question'
    parent: parent widget (MainWindow or dialog)
    """
    dlg = QtWidgets.QMessageBox(parent)
    dlg.setWindowTitle(title or '')
    if kind == 'warning':
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    elif kind == 'critical':
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    elif kind == 'question':
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Question)
    else:
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Information)
    dlg.setText(text or '')

    theme = _resolve_theme_from(parent)
    if theme is None and hasattr(parent, 'parent'):
        theme = _resolve_theme_from(getattr(parent, 'parent'))

    if theme is not None:
        try:
            bg = theme.color('surface_color')
            textc = theme.color('text_color')
            border = theme.color('border_color')
            primary = theme.color('primary_color')
            sheet = f"""
            QMessageBox {{ background: {bg}; color: {textc}; }}
            QLabel {{ color: {textc}; }}
            QPushButton {{ background: transparent; color: {textc}; border: 1px solid {border}; border-radius:6px; padding:6px 10px }}
            QPushButton:hover {{ background: {border}; }}
            """
            dlg.setStyleSheet(sheet)
        except Exception:
            pass

    dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
    dlg.exec()


def detect_country_from_number(number: str) -> Dict[str, str]:
    """Intenta inferir el código de país y nombre a partir del número.

    No usa librerías externas; coincide por prefijos comunes.
    Devuelve dict {'code': '52', 'country': 'Mexico'} o vacío si no se reconoce.
    """
    if not number:
        return {}
    s = ''.join(ch for ch in number if ch.isdigit())
    if s.startswith('00'):
        s = s[2:]
    if s.startswith('0') and not s.startswith('00'):
        # números locales sin prefijo
        return {}

    # mapping simple (prefijos más comunes) - puede ampliarse
    mapping = {
        '1': 'United States / Canada',
        '7': 'Russia',
        '20': 'Egypt',
        '30': 'Greece',
        '34': 'Spain',
        '39': 'Italy',
        '44': 'United Kingdom',
        '49': 'Germany',
        '52': 'Mexico',
        '54': 'Argentina',
        '55': 'Brazil',
        '57': 'Colombia',
        '58': 'Venezuela',
        '91': 'India',
        '98': 'Iran',
    }

    # Try longest-match: check 3,2,1 digits
    for l in (3, 2, 1):
        if len(s) >= l:
            code = s[:l]
            if code in mapping:
                return {'code': code, 'country': mapping[code]}
    return {}


def normalize_phone(number: str) -> str:
    """Normalize a phone number by removing spaces, plus signs and any non-digit characters.

    Example: "+57 316 3539221" -> "573163539221"
    """
    if not number:
        return ''
    return ''.join(ch for ch in str(number) if ch.isdigit())


class ProfileDialog(QtWidgets.QDialog):
    """Ventana de perfil elegante que muestra código de país, número y país detectado."""
    def __init__(self, code: str, local: str, country: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle('Perfil')
        self.setMinimumSize(420, 160)
        # Remove native title bar, use custom header like main window
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Rounded container so dialog looks like main window panel
        self.container = QtWidgets.QFrame()
        self.container.setObjectName('dialogContainer')
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)

        # Custom header (icon + title + close) to match app style
        header = QtWidgets.QFrame()
        header.setObjectName('dialogTitleBar')
        header_h = QtWidgets.QHBoxLayout(header)
        header_h.setContentsMargins(6, 0, 6, 0)
        header_h.setSpacing(8)
        icon_path = resource_path('..', 'assets', 'icon.png')
        self.header_icon = QtWidgets.QLabel()
        self.header_icon.setFixedSize(20, 20)
        if os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path).scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self.header_icon.setPixmap(pix)
        header_h.addWidget(self.header_icon)
        self.header_title = QtWidgets.QLabel('Información de la cuenta')
        self.header_title.setObjectName('dialogTitle')
        header_h.addWidget(self.header_title)
        header_h.addStretch()
        self.header_close = QtWidgets.QPushButton('✕')
        self.header_close.setObjectName('dialogClose')
        self.header_close.setFixedSize(30, 26)
        self.header_close.clicked.connect(self.close)
        header_h.addWidget(self.header_close)
        container_layout.addWidget(header)

        # Content: show code, local number (formatted) and country
        container_layout.addWidget(QtWidgets.QLabel('Código:'))
        display_code = f"+{code}" if code else '(no configurado)'
        self.lbl_code = QtWidgets.QLabel(display_code)
        container_layout.addWidget(self.lbl_code)

        container_layout.addWidget(QtWidgets.QLabel('Número:'))
        # format local number with a space after first 3 digits if appropriate
        if local and len(local) > 3:
            formatted_local = local[:3] + ' ' + local[3:]
        else:
            formatted_local = local or '(no configurado)'
        self.lbl_number = QtWidgets.QLabel(formatted_local)
        container_layout.addWidget(self.lbl_number)

        container_layout.addWidget(QtWidgets.QLabel('País:'))
        self.lbl_country = QtWidgets.QLabel(country or '(no disponible)')
        container_layout.addWidget(self.lbl_country)

        row = QtWidgets.QHBoxLayout()
        row.addStretch()
        btn_copy = QtWidgets.QPushButton('Copiar número')
        btn_close2 = QtWidgets.QPushButton('Cerrar')
        row.addWidget(btn_copy)
        row.addWidget(btn_close2)
        container_layout.addLayout(row)

        btn_close2.clicked.connect(self.close)
        btn_copy.clicked.connect(self._copy_number)

        layout.addWidget(self.container)

        # Drag handling on header (make frame draggable)
        self._drag_pos = None
        header.mousePressEvent = self._title_mouse_press
        header.mouseMoveEvent = self._title_mouse_move

    def _copy_number(self):
        cb = QtWidgets.QApplication.clipboard()
        # copy a normalized version: country code + local digits without spaces
        parts = []
        try:
            code_text = self.lbl_code.text() if hasattr(self, 'lbl_code') else ''
            local_text = self.lbl_number.text() if hasattr(self, 'lbl_number') else ''
            # extract digits
            code_digits = ''.join(ch for ch in str(code_text) if ch.isdigit())
            local_digits = ''.join(ch for ch in str(local_text) if ch.isdigit())
            if code_digits:
                parts.append(code_digits)
            if local_digits:
                parts.append(local_digits)
            out = ''.join(parts) if parts else (local_text or code_text or '')
            cb.setText(out)
        except Exception:
            cb.setText(self.lbl_number.text())

    def apply_theme(self, theme: Theme):
        try:
            if isinstance(theme, Theme):
                bg = theme.color('surface_color')
                text = theme.color('text_color')
                border = theme.color('border_color')
                primary = theme.color('primary_color')
            elif isinstance(theme, dict):
                bg = theme.get('surface_color', '#ffffff')
                text = theme.get('text_color', '#000000')
                border = theme.get('border_color', '#e6e6e6')
                primary = theme.get('primary_color', '#1F6F4B')
            else:
                return
            sheet = f"""
            QDialog {{ background: transparent; }}
            QFrame#dialogContainer {{ background: {bg}; border-radius: 10px; border: 1px solid {border}; }}
            QFrame#dialogTitleBar {{ background: transparent; }}
            QLabel#dialogTitle {{ color: {primary}; font-weight:700; font-size:16px; }}
            QLabel {{ color: {text}; }}
            QPushButton {{ background: transparent; color: {text}; border: 1px solid {border}; padding:6px 10px; border-radius:6px }}
            QPushButton:hover {{ background: {border}; }}
            QPushButton#dialogClose {{ background: transparent; border: none; color: {text}; font-size: 14px; }}
            QPushButton#dialogClose:hover {{ background: {border}; color: {text}; }}
            QLabel#dialogIcon {{ border-radius: 4px; }}
            """
            self.setStyleSheet(sheet)
        except Exception:
            pass

    def _title_mouse_press(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


class SettingsDialog(QtWidgets.QDialog):
    """Diálogo profesional para editar `config.json` con estilos adaptativos."""
    def __init__(self, config_path: str, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.setWindowTitle('Configuración')
        self.setMinimumSize(480, 300)
        # Use frameless custom dialog like main window
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # rounded container
        self.container = QtWidgets.QFrame()
        self.container.setObjectName('dialogContainer')
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)

        # Custom header
        header = QtWidgets.QFrame()
        header.setObjectName('dialogTitleBar')
        hh = QtWidgets.QHBoxLayout(header)
        hh.setContentsMargins(6, 0, 6, 0)
        hh.setSpacing(8)
        icon_path = resource_path('..', 'assets', 'icon.png')
        self.header_icon = QtWidgets.QLabel()
        self.header_icon.setFixedSize(20, 20)
        if os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path).scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self.header_icon.setPixmap(pix)
        hh.addWidget(self.header_icon)
        title_lbl = QtWidgets.QLabel('Ajustes de conexión')
        title_lbl.setObjectName('dialogTitle')
        hh.addWidget(title_lbl)
        hh.addStretch()
        self.header_close = QtWidgets.QPushButton('✕')
        self.header_close.setObjectName('dialogClose')
        self.header_close.setFixedSize(30, 26)
        self.header_close.clicked.connect(self.reject)
        hh.addWidget(self.header_close)
        container_layout.addWidget(header)

        form = QtWidgets.QFormLayout()
        self.input_phone = QtWidgets.QLineEdit()
        self.input_id = QtWidgets.QLineEdit()
        self.input_token = QtWidgets.QLineEdit()
        # create explicit labels so we can style them (were too dark before)
        lbl_phone = QtWidgets.QLabel('Número de teléfono:')
        lbl_phone.setObjectName('formLabel')
        lbl_id = QtWidgets.QLabel('ID:')
        lbl_id.setObjectName('formLabel')
        lbl_token = QtWidgets.QLabel('Token:')
        lbl_token.setObjectName('formLabel')
        form.addRow(lbl_phone, self.input_phone)
        form.addRow(lbl_id, self.input_id)
        form.addRow(lbl_token, self.input_token)
        container_layout.addLayout(form)
        layout.addWidget(self.container)

        # Buttons
        row = QtWidgets.QHBoxLayout()
        row.addStretch()
        self.btn_cancel = QtWidgets.QPushButton('Cancelar')
        self.btn_save = QtWidgets.QPushButton('Guardar')
        row.addWidget(self.btn_cancel)
        row.addWidget(self.btn_save)
        container_layout.addLayout(row)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self._on_save)

        # Drag handlers
        self._drag_pos = None
        header.mousePressEvent = self._title_mouse_press
        header.mouseMoveEvent = self._title_mouse_move

        self._load()

    def _load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.input_phone.setText(data.get('phone_number', ''))
                self.input_id.setText(data.get('id', ''))
                self.input_token.setText(data.get('token', ''))
        except Exception:
            pass

    def _on_save(self):
        data = {
            'phone_number': self.input_phone.text().strip(),
            'id': self.input_id.text().strip(),
            'token': self.input_token.text().strip()
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            show_themed_message(self, 'information', 'Guardado', 'Configuración guardada.')
            self.accept()
        except Exception as e:
            show_themed_message(self, 'critical', 'Error', f'No se pudo guardar: {e}')

    def apply_theme(self, theme: Theme):
        try:
            if isinstance(theme, Theme):
                bg = theme.color('surface_color')
                text = theme.color('text_color')
                border = theme.color('border_color')
                primary = theme.color('primary_color')
            elif isinstance(theme, dict):
                bg = theme.get('surface_color', '#ffffff')
                text = theme.get('text_color', '#000000')
                border = theme.get('border_color', '#e6e6e6')
                primary = theme.get('primary_color', '#1F6F4B')
            else:
                return
            sheet = f"""
            QDialog {{ background: transparent; }}
            QFrame#dialogContainer {{ background: {bg}; border-radius: 10px; border: 1px solid {border}; }}
            QFrame#dialogTitleBar {{ background: transparent; }}
            QLabel#dialogTitle {{ color: {primary}; font-weight:800; font-size:16px; }}
            QLabel#formLabel {{ color: {text}; font-weight:600; }}
            QLineEdit {{ background: {bg}; color: {text}; border: 1px solid {border}; border-radius:8px; padding:8px; }}
            QPushButton {{ background: transparent; color: {text}; border: 1px solid {border}; padding:8px 12px; border-radius:8px }}
            QPushButton:hover {{ background: {border}; }}
            QPushButton#dialogClose:hover {{ background: {border}; color: {text}; }}
            QPushButton#btn_save {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {primary}, stop:1 {primary}); color: #fff; font-weight:700 }}
            QPushButton#dialogClose {{ background: transparent; border: none; color: {text}; font-size: 14px; }}
            """
            self.setStyleSheet(sheet)
        except Exception:
            pass

    def _title_mouse_press(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


class HistoryDialog(QtWidgets.QDialog):
    """Diálogo que muestra historial y permite exportarlo desde la propia ventana."""
    def __init__(self, history_path: str, parent=None):
        super().__init__(parent)
        self.history_path = history_path
        self.setWindowTitle('Historial de actividad')
        self.setMinimumSize(560, 380)
        # Frameless to use custom title like other dialogs
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # Container
        self.container = QtWidgets.QFrame()
        self.container.setObjectName('dialogContainer')
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)

        # Custom header
        header = QtWidgets.QFrame()
        header.setObjectName('dialogTitleBar')
        hh = QtWidgets.QHBoxLayout(header)
        hh.setContentsMargins(6, 0, 6, 0)
        hh.setSpacing(8)
        icon_path = resource_path('..', 'assets', 'icon.png')
        self.header_icon = QtWidgets.QLabel()
        self.header_icon.setFixedSize(20, 20)
        if os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path).scaled(20, 20, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self.header_icon.setPixmap(pix)
        hh.addWidget(self.header_icon)
        title_lbl = QtWidgets.QLabel('Historial')
        title_lbl.setObjectName('dialogTitle')
        hh.addWidget(title_lbl)
        hh.addStretch()
        self.header_close = QtWidgets.QPushButton('✕')
        self.header_close.setObjectName('dialogClose')
        self.header_close.setFixedSize(30, 26)
        self.header_close.clicked.connect(self.close)
        hh.addWidget(self.header_close)
        container_layout.addWidget(header)

        self.viewer = QtWidgets.QPlainTextEdit()
        self.viewer.setReadOnly(True)
        container_layout.addWidget(self.viewer, 1)

        row = QtWidgets.QHBoxLayout()
        row.addStretch()
        self.btn_export = QtWidgets.QPushButton('Exportar')
        self.btn_close = QtWidgets.QPushButton('Cerrar')
        row.addWidget(self.btn_export)
        row.addWidget(self.btn_close)
        container_layout.addLayout(row)

        self.btn_close.clicked.connect(self.close)
        self.btn_export.clicked.connect(self._export)

        layout.addWidget(self.container)

        self._load()

        # Drag handlers
        self._drag_pos = None
        header.mousePressEvent = self._title_mouse_press
        header.mouseMoveEvent = self._title_mouse_move

    def _load(self):
        try:
            if os.path.exists(self.history_path):
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self.viewer.setPlainText(f.read())
            else:
                self.viewer.setPlainText('No hay historial aún.')
        except Exception:
            self.viewer.setPlainText('Error cargando historial.')

    def _export(self):
        dest, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Guardar historial como', os.path.expanduser('~'), 'Text files (*.txt);;All files (*.*)')
        if dest:
            try:
                with open(dest, 'w', encoding='utf-8') as out:
                    out.write(self.viewer.toPlainText())
                show_themed_message(self, 'information', 'Exportado', f'Historial guardado en: {dest}')
            except Exception as e:
                show_themed_message(self, 'critical', 'Error', f'No se pudo guardar: {e}')

    def apply_theme(self, theme: Theme):
        try:
            if isinstance(theme, Theme):
                bg = theme.color('surface_color')
                text = theme.color('text_color')
                border = theme.color('border_color')
                primary = theme.color('primary_color')
            elif isinstance(theme, dict):
                bg = theme.get('surface_color', '#ffffff')
                text = theme.get('text_color', '#000000')
                border = theme.get('border_color', '#e6e6e6')
                primary = theme.get('primary_color', '#1F6F4B')
            else:
                return
            sheet = f"""
            QDialog {{ background: transparent; }}
            QFrame#dialogContainer {{ background: {bg}; border-radius: 10px; border: 1px solid {border}; }}
            QLabel[role='title'] {{ color: {primary}; font-weight:800; font-size:16px; }}
            QPlainTextEdit {{ background: {bg}; color: {text}; border: 1px solid {border}; border-radius:8px; padding:8px; }}
            QPushButton {{ background: transparent; color: {text}; border: 1px solid {border}; padding:8px 12px; border-radius:8px }}
            QPushButton:hover {{ background: {border}; }}
            QPushButton#dialogClose:hover {{ background: {border}; color: {text}; }}
            QPushButton#dialogClose {{ background: transparent; border: none; color: {text}; font-size: 14px; }}
            """
            self.setStyleSheet(sheet)
        except Exception:
            pass

    def _title_mouse_press(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


class WelcomeDialog(QtWidgets.QDialog):
    """Diálogo flotante para introducir Número, ID y Token y guardar en config.json.

    Características nuevas:
    - Frameless con barra de título personalizada.
    - Contenedor interior para mostrar márgenes laterales.
    - Más alto para que el tutorial incrustado sea visible.
    - Botón 'Iniciar' con fondo negro y texto blanco.
    """
    saved = QtCore.pyqtSignal(dict)

    def __init__(self, config_path: str, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.setWindowTitle('Configuración inicial - PandaMessage')
        flags = QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.Tool
        # Frameless para permitir barra de título personalizada
        self.setWindowFlags(flags | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        # Fondo translúcido para poder mostrar el borde redondeado del contenedor
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Más alto y con márgenes visibles
        self.setFixedSize(520, 670)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        # Contenedor interior con fondo y border-radius para mostrar márgenes alrededor
        self.container = QtWidgets.QFrame()
        self.container.setObjectName('welcomeContainer')
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(14, 12, 14, 14)
        container_layout.setSpacing(10)

        # Barra de título personalizada
        self.title_bar = QtWidgets.QFrame()
        self.title_bar.setObjectName('dialogTitleBar')
        self.title_bar.setFixedHeight(36)
        title_h = QtWidgets.QHBoxLayout(self.title_bar)
        title_h.setContentsMargins(8, 0, 8, 0)
        title_h.setSpacing(8)

        # icon pequeño
        icon_path = resource_path('..', 'assets', 'icon.png')
        self.dlg_icon = QtWidgets.QLabel()
        self.dlg_icon.setFixedSize(18, 18)
        if os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path).scaled(18, 18, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            self.dlg_icon.setPixmap(pix)
        title_h.addWidget(self.dlg_icon)

        self.dlg_title = QtWidgets.QLabel('Bienvenido a PandaMessage')
        self.dlg_title.setObjectName('dialogTitle')
        title_h.addWidget(self.dlg_title)
        title_h.addStretch()

        self.dlg_close = QtWidgets.QPushButton('✕')
        self.dlg_close.setFixedSize(34, 28)
        self.dlg_close.setObjectName('dialogClose')
        self.dlg_close.clicked.connect(self.close)
        title_h.addWidget(self.dlg_close)

        container_layout.addWidget(self.title_bar)

        # Contenido del diálogo
        info_lbl = QtWidgets.QLabel('<b>Configura tu cuenta</b>')
        info_lbl.setProperty('role', 'title')
        container_layout.addWidget(info_lbl)

        container_layout.addWidget(QtWidgets.QLabel('Número De telefono:'))
        self.input_phone = QtWidgets.QLineEdit()
        self.input_phone.setPlaceholderText('Número (ej: 521XXXXXXXXXX)')
        container_layout.addWidget(self.input_phone)

        container_layout.addWidget(QtWidgets.QLabel('ID:'))
        self.input_id = QtWidgets.QLineEdit()
        container_layout.addWidget(self.input_id)

        container_layout.addWidget(QtWidgets.QLabel('Token:'))
        self.input_token = QtWidgets.QLineEdit()
        container_layout.addWidget(self.input_token)

        # Tutorial incrustado
        tutorial_heading = QtWidgets.QLabel('Tutorial rápido')
        tutorial_heading.setProperty('role', 'title')
        container_layout.addWidget(tutorial_heading)

        self.tutorial_view = QtWidgets.QTextBrowser()
        self.tutorial_view.setOpenExternalLinks(True)
        self.tutorial_view.setMinimumHeight(200)
        self.tutorial_view.setHtml(
            """
            <h4 style='margin:0 0 6px 0;color:inherit;'>Cómo obtener ID y Token (UltraMsg)</h4>
            <ol>
              <li>Regístrate o inicia sesión en <a href='https://ultramsg.com'>UltraMsg</a>.</li>
              <li>En tu panel, ve a la sección <b>API / Instance</b>.</li>
              <li>Crea o selecciona una instancia y copia el <b>ID</b> mostrado.</li>
              <li>Genera o copia el <b>Token</b> (credenciales/API token).</li>
              <li>Usa el número asociado en formato internacional (ej: <code>521XXXXXXXXXX</code>).</li>
              <li>Pega ID y Token en los campos arriba y pulsa <b>Iniciar</b>.</li>
            </ol>
            """
        )
        container_layout.addWidget(self.tutorial_view)

        # Botón iniciar al final
        row = QtWidgets.QHBoxLayout()
        row.addStretch()
        self.btn_start = QtWidgets.QPushButton('Iniciar')
        self.btn_start.setObjectName('btnStart')
        self.btn_start.setFixedHeight(40)
        self.btn_start.clicked.connect(self.on_start)
        row.addWidget(self.btn_start)
        container_layout.addLayout(row)

        root.addWidget(self.container)

        # cargar valores previos si existen
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.input_phone.setText(data.get('phone_number', ''))
                    self.input_id.setText(data.get('id', ''))
                    self.input_token.setText(data.get('token', ''))
        except Exception:
            pass

        # Estilos iniciales (se pueden sobrescribir por apply_theme)
        self.setStyleSheet("""
        QDialog { background: transparent; }
        QFrame#welcomeContainer { background: #0f1618; border-radius: 12px; }
        QLabel { color: #e6f0ef; }
        QLabel[role='title'] { font-size:15px; font-weight:700; color: #ffffff; }
        QLabel#dialogTitle { font-weight:700; color: #ffffff; }
        QLineEdit { background: #121212; color: #fff; border: 1px solid #2a2a2a; border-radius: 8px; padding: 8px; }
        QTextBrowser { background: transparent; color: #dfecec; border: none; }
        QPushButton#btnStart { background: #000000; color: #ffffff; font-weight: 800; border-radius: 8px; padding: 8px 14px; }
        QPushButton#dialogClose { background: transparent; border: none; color: #ffffff; font-size: 14px; }
        QFrame#dialogTitleBar { background: transparent; }
        """)

        # Drag handling
        self._drag_pos = None
        self.title_bar.mousePressEvent = self._title_mouse_press
        self.title_bar.mouseMoveEvent = self._title_mouse_move

        # Aplicar tema nocturno por defecto si existe
        try:
            dark_path = resource_path('..', 'themes', 'dark_theme.json')
            if os.path.exists(dark_path):
                dark_theme = Theme(dark_path)
                self.apply_theme(dark_theme)
        except Exception:
            pass

    def _title_mouse_press(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def on_start(self):
        phone = self.input_phone.text().strip()
        idv = self.input_id.text().strip()
        token = self.input_token.text().strip()
        if not phone or not idv or not token:
            show_themed_message(self, 'warning', 'Faltan datos', 'Completa Número, ID y Token.')
            return
        # Normalize phone before saving (store digits only, no spaces or '+')
        clean_phone = normalize_phone(phone)
        data = {'phone_number': clean_phone, 'id': idv, 'token': token}
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            # emit saved signal if present
            try:
                self.saved.emit(data)
            except Exception:
                pass
            show_themed_message(self, 'information', 'Guardado', 'Configuración guardada correctamente.')
            self.close()
        except Exception:
            show_themed_message(self, 'critical', 'Error', 'No se pudo guardar config.json')

    def apply_theme(self, theme: Theme):
        try:
            if isinstance(theme, Theme):
                bg = theme.color('surface_color')
                primary = theme.color('primary_color')
                border = theme.color('border_color')
                text = theme.color('text_color')
                accent = theme.color('accent_color')
            elif isinstance(theme, dict):
                bg = theme.get('surface_color', '#0f1618')
                primary = theme.get('primary_color', '#1F6F4B')
                border = theme.get('border_color', '#222')
                text = theme.get('text_color', '#e6f0ef')
                accent = theme.get('accent_color', '#2e8b57')
            else:
                return

            sheet = f"""
            QDialog {{ background: transparent; }}
            QFrame#welcomeContainer {{ background: {bg}; border-radius: 12px; border: 1px solid {border}; }}
            QFrame#dialogTitleBar {{ background: transparent; }}
            QLabel {{ color: {text}; }}
            QLabel[role='title'] {{ color: {text}; }}
            QLabel#dialogTitle {{ color: {text}; font-weight:700; }}
            QLineEdit {{ background: {bg}; color: {text}; border: 1px solid {border}; border-radius: 8px; padding: 8px; }}
            QTextBrowser {{ background: transparent; color: {text}; border: none; }}
            QPushButton#btnStart {{ background: #000000; color: #ffffff; font-weight: 800; border-radius: 8px; padding: 8px 14px; }}
            QPushButton#dialogClose {{ background: transparent; border: none; color: {text}; font-size: 14px; }}
            QPushButton#dialogClose:hover {{ background: {border}; color: {text}; }}
            """
            self.setStyleSheet(sheet)
        except Exception:
            pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, themes_dir=None):
        super().__init__()
        self.setWindowTitle('PandaMessage - Envío WhatsApp (UI)')
        self.resize(1000, 720)

        # Set window icon from assets
        icon_path = resource_path('..', 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # themes
        self.themes_dir = themes_dir or resource_path('..', 'themes')
        self.themes = self.load_themes()
        self.theme_keys = list(self.themes.keys())
        self.current_theme_index = 0
        self.current_theme_key = self.theme_keys[self.current_theme_index] if self.theme_keys else None
        self.current_theme = self.themes.get(self.current_theme_key) if self.current_theme_key else None

        # ruta del archivo de configuración en ubicación escribible
        self.config_path = get_user_config_path()
        
        # Si no existe config en ubicación de usuario, intentar copiar desde instalación
        if not os.path.exists(self.config_path):
            try:
                install_config_path = resource_path('..', 'config.json')
                if os.path.exists(install_config_path):
                    import shutil
                    shutil.copy2(install_config_path, self.config_path)
            except Exception:
                pass  # Si no se puede copiar, se creará nuevo config
                
        self.config = self.load_config()
        self.configured = bool(self.config.get('phone_number') and self.config.get('id') and self.config.get('token'))

        # inicializar UI
        self.init_ui()
        if self.current_theme:
            self.apply_theme(self.current_theme)

    def load_themes(self):
        themes = {}
        if not os.path.isdir(self.themes_dir):
            return themes
        for fname in os.listdir(self.themes_dir):
            if fname.endswith('.json'):
                path = os.path.join(self.themes_dir, fname)
                try:
                    themes[fname.replace('.json', '')] = Theme(path)
                except Exception:
                    pass
        return themes

    # ---- Perfil / Configuración / Historial handlers ----
    def show_profile(self):
        cfg = self.load_config() or {}
        raw_phone = cfg.get('phone_number', '')
        # Normalize and detect country
        norm = normalize_phone(raw_phone)
        detected = detect_country_from_number(norm)
        country_name = detected.get('country') if detected else ''
        country_code = detected.get('code') if detected else ''

        # Build code and local parts for the dialog
        if norm and country_code and norm.startswith(country_code):
            local = norm[len(country_code):]
            code_display = country_code
        else:
            # If cannot detect, leave code empty and show raw as local
            code_display = ''
            local = raw_phone or ''

        # Mostrar diálogo elegante con código, local y país
        dlg = ProfileDialog(code_display, local, country_name or '(no disponible)')
        if self.current_theme:
            dlg.apply_theme(self.current_theme)
        dlg.exec()

    def show_settings(self):
        dlg = SettingsDialog(self.config_path, parent=self)
        if self.current_theme:
            dlg.apply_theme(self.current_theme)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # recargar y aplicar
            newcfg = self.load_config()
            self.on_config_saved(newcfg or {})

    def show_history(self):
        hist_path = os.path.abspath(resource_path('..', 'database', 'history.txt'))
        # ensure database dir exists
        try:
            os.makedirs(os.path.dirname(hist_path), exist_ok=True)
        except Exception:
            pass
        dlg = HistoryDialog(hist_path, parent=self)
        if self.current_theme:
            dlg.apply_theme(self.current_theme)
        dlg.exec()

    def init_ui(self):
        # Eliminar barra de título nativa
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        # Widget central y layout raíz vertical
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root_v = QtWidgets.QVBoxLayout(central)
        root_v.setContentsMargins(0, 0, 0, 0)
        root_v.setSpacing(0)

        # Barra de título personalizada
        self.title_bar = QtWidgets.QFrame()
        self.title_bar.setObjectName('customTitleBar')
        self.title_bar.setFixedHeight(38)
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(8, 0, 8, 0)
        title_layout.setSpacing(8)

        # Icono (con border-radius)
        icon_path = resource_path('..', 'assets', 'icon.png')
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(24, 24)
        if os.path.exists(icon_path):
            orig = QtGui.QPixmap(icon_path).scaled(24, 24, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
            size = orig.size()
            rounded = QtGui.QPixmap(size)
            rounded.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(rounded)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            path = QtGui.QPainterPath()
            # usar un radio pequeño para que no sea completamente circular
            radius = min(size.width(), size.height()) * 0.23  # ~5.5px en 24x24
            path.addRoundedRect(QtCore.QRectF(0.0, 0.0, float(size.width()), float(size.height())), float(radius), float(radius))
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, orig)
            painter.end()
            self.icon_label.setPixmap(rounded)
        title_layout.addWidget(self.icon_label)

        # Título
        self.title_label = QtWidgets.QLabel('PandaMessage')
        self.title_label.setObjectName('customTitle')
        self.title_label.setStyleSheet('font-weight: 600; font-size: 15px;')
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Botones de ventana
        self.btn_min = QtWidgets.QPushButton('-')
        self.btn_min.setFixedSize(32, 28)
        self.btn_min.setObjectName('btnMin')
        self.btn_min.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.btn_min)

        self.btn_max = QtWidgets.QPushButton('□')
        self.btn_max.setFixedSize(32, 28)
        self.btn_max.setObjectName('btnMax')
        self.btn_max.clicked.connect(self.toggle_max_restore)
        title_layout.addWidget(self.btn_max)

        self.btn_close = QtWidgets.QPushButton('✕')
        self.btn_close.setFixedSize(32, 28)
        self.btn_close.setObjectName('btnClose')
        self.btn_close.clicked.connect(self.close)
        title_layout.addWidget(self.btn_close)

        # Permitir mover la ventana arrastrando la barra
        self.offset = None
        self.title_bar.mousePressEvent = self.title_bar_mouse_press
        self.title_bar.mouseMoveEvent = self.title_bar_mouse_move
        self.title_bar.mouseDoubleClickEvent = self.title_bar_mouse_double_click

        root_v.addWidget(self.title_bar)

        # Layout horizontal principal (sidebar + main)
        root_h = QtWidgets.QHBoxLayout()
        root_h.setContentsMargins(0, 0, 0, 0)
        root_v.addLayout(root_h)

        # Si no está configurado, mostrar diálogo flotante
        if not self.configured:
            dlg = WelcomeDialog(self.config_path, parent=self)
            dlg.saved.connect(self.on_config_saved)
            dlg.show()

        # ...existing code for sidebar and main panel...
        # Left navigation (sidebar)
        nav_frame = QtWidgets.QFrame()
        nav_frame.setObjectName('navFrame')
        nav_frame.setFixedWidth(160)
        nav_layout = QtWidgets.QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(10)

        nav_title = QtWidgets.QLabel('Panda')
        nav_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        nav_title.setObjectName('navTitle')
        nav_layout.addWidget(nav_title)

        # Navigation buttons
        btn_cfg = QtWidgets.QPushButton('Configuración')
        btn_hist = QtWidgets.QPushButton('Historial')
        btn_profile = QtWidgets.QPushButton('Perfil')
        for b in (btn_cfg, btn_hist, btn_profile):
            b.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            b.setMinimumHeight(36)
            nav_layout.addWidget(b)

        # conectar acciones de sidebar
        btn_profile.clicked.connect(self.show_profile)
        btn_cfg.clicked.connect(self.show_settings)
        btn_hist.clicked.connect(self.show_history)

        nav_layout.addStretch()

        # Single theme-cycle button at the bottom
        self.btn_cycle_theme = QtWidgets.QPushButton('Cambiar tema')
        self.btn_cycle_theme.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btn_cycle_theme.setMinimumHeight(36)
        self.btn_cycle_theme.clicked.connect(self.cycle_theme)
        nav_layout.addWidget(self.btn_cycle_theme)

        root_h.addWidget(nav_frame)

        # Main panel
        main_frame = QtWidgets.QFrame()
        main_layout = QtWidgets.QVBoxLayout(main_frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        # Split main area into two columns: Numbers (left) | Message (right)
        content_h = QtWidgets.QHBoxLayout()

        # Left: small vertical box for numbers
        left_frame = QtWidgets.QFrame()
        left_layout = QtWidgets.QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 8, 0)

        lbl_nums = QtWidgets.QLabel('Números')
        lbl_nums.setObjectName('sectionLabel')
        self.txt_numbers = QtWidgets.QPlainTextEdit()
        self.txt_numbers.setPlaceholderText('Un número por línea\n(Soporta pegar desde TXT/CSV)')
        self.txt_numbers.setMaximumWidth(240)
        # Allow drag & drop of .txt files and provide a load button
        self.txt_numbers.setAcceptDrops(True)
        # install event filter so MainWindow.eventFilter can handle drops
        try:
            self.txt_numbers.installEventFilter(self)
        except Exception:
            pass
        left_layout.addWidget(lbl_nums)
        left_layout.addWidget(self.txt_numbers)

        file_h = QtWidgets.QHBoxLayout()
        file_h.setContentsMargins(0, 0, 0, 0)
        self.btn_load_file = QtWidgets.QPushButton('Cargar .txt')
        self.btn_load_file.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btn_load_file.setMinimumHeight(30)
        self.btn_load_file.clicked.connect(self.load_numbers_from_file)
        file_h.addWidget(self.btn_load_file)
        file_h.addStretch()
        left_layout.addLayout(file_h)

        # Right: message editor and controls
        right_frame = QtWidgets.QFrame()
        right_layout = QtWidgets.QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)

        lbl_msg = QtWidgets.QLabel('Mensaje')
        lbl_msg.setObjectName('sectionLabel')
        self.txt_message = QtWidgets.QPlainTextEdit()
        self.txt_message.setPlaceholderText('Escribe tu mensaje aquí... (soporta emojis y símbolos)')
        self.txt_message.setMinimumHeight(220)

        # Controls row (send button aligned right)
        controls_h = QtWidgets.QHBoxLayout()
        controls_h.addStretch()
        self.btn_send = QtWidgets.QPushButton('Enviar ahora')
        self.btn_send.setObjectName('sendButton')
        self.btn_send.setFixedSize(120, 42)
        controls_h.addWidget(self.btn_send)
        self.btn_send.setToolTip('Enviar el mensaje a los números listados (simulado en UI)')

        # Status panel under send
        self.status_list = QtWidgets.QListWidget()
        self.status_list.setFixedHeight(140)
        self.status_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.status_list.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        right_layout.addWidget(lbl_msg)
        right_layout.addWidget(self.txt_message)
        right_layout.addLayout(controls_h)
        right_layout.addWidget(self.status_list)

        content_h.addWidget(left_frame)
        content_h.addWidget(right_frame, 1)

        main_layout.addLayout(content_h)

        root_h.addWidget(main_frame)

        # Signals and initial states
        self.btn_send.clicked.connect(self.on_send_clicked)

        # Minimal styling placeholders
        self.setStyleSheet(self.default_stylesheet())

    def toggle_max_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # File loading helpers for numbers area
    def load_numbers_from_file(self):
        """Open a file dialog restricted to .txt and load its contents into the numbers box."""
        dest, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Seleccionar archivo .txt', os.path.expanduser('~'), 'Text files (*.txt)')
        if not dest:
            return
        try:
            with open(dest, 'r', encoding='utf-8') as f:
                content = f.read()
            # Normalize line endings and set text
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            # Join with single newline and place into the numbers field
            self.txt_numbers.setPlainText('\n'.join(lines))
            self.append_status(f'Cargado {len(lines)} números desde {os.path.basename(dest)}')
        except Exception as e:
            show_themed_message(self, 'critical', 'Error', f'No se pudo leer el archivo: {e}')

    # Enable drag enter/drag move for the numbers text area
    def eventFilter(self, obj, event):
        # allow drag/drop on txt_numbers
        try:
            if obj is self.txt_numbers:
                from PyQt6 import QtGui as _QtGui
                if event.type() == _QtGui.QDragEnterEvent.Type.DragEnter:
                    event.accept()
                    return True
                if event.type() == _QtGui.QDropEvent.Type.Drop:
                    mime = event.mimeData()
                    if mime.hasUrls():
                        for url in mime.urls():
                            path = url.toLocalFile()
                            if path.lower().endswith('.txt'):
                                try:
                                    with open(path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    lines = [l.strip() for l in content.splitlines() if l.strip()]
                                    existing = self.txt_numbers.toPlainText().strip()
                                    combined = '\n'.join(filter(None, [existing, '\n'.join(lines)])).strip()
                                    self.txt_numbers.setPlainText(combined)
                                    self.append_status(f'Cargado {len(lines)} números desde arrastre: {os.path.basename(path)}')
                                except Exception:
                                    pass
                        return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def title_bar_mouse_press(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def title_bar_mouse_move(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)

    def title_bar_mouse_double_click(self, event):
        self.toggle_max_restore()

    # Config file helpers
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_config(self):
        data = {
            'phone_number': self.input_phone.text().strip(),
            'id': self.input_id.text().strip(),
            'token': self.input_token.text().strip()
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.config = data
            self.configured = True
            return True
        except Exception:
            return False

    def show_tutorial_dialog(self):
        text = (
            "Pasos para obtener ID y Token desde UltraMsg:\n\n"
            "1) Regístrate o inicia sesión en https://ultramsg.com\n"
            "2) En tu panel, ve a 'API' o 'Instance' (según interfaz).\n"
            "3) Crea una nueva instancia o selecciona la existente.\n"
            "4) Copia el 'ID' mostrado para tu instancia.\n"
            "5) Genera o copia el 'Token' (API token) en la sección de credenciales.\n"
            "6) Coloca el número de teléfono que usarás para enviar mensajes en el formato internacional (ej: 521XXXXXXXXXX).\n"
            "7) Vuelve a la app, pega ID y Token y presiona 'Iniciar'.\n\n"
            "Nota: UltraMsg muestra instrucciones específicas en su panel; si tienen calculadora de puerto o instrucciones adicionales sigue las indicaciones de su sitio."
        )
        show_themed_message(self, 'information', 'Tutorial - Obtener ID y Token (UltraMsg)', text)

    def on_start_clicked(self):
        # Validar campos mínimos
        phone = self.input_phone.text().strip()
        idv = self.input_id.text().strip()
        token = self.input_token.text().strip()
        if not phone or not idv or not token:
            show_themed_message(self, 'warning', 'Faltan datos', 'Por favor completa Número, ID y Token antes de iniciar.')
            return
        ok = self.save_config()
        if ok:
            show_themed_message(self, 'information', 'Guardado', 'Configuración guardada correctamente. Puedes comenzar a usar la aplicación.')
            try:
                self.welcome_frame.hide()
            except Exception:
                pass
        else:
            show_themed_message(self, 'critical', 'Error', 'No se pudo guardar la configuración en disco.')

    def default_stylesheet(self):
        return """
        QMainWindow { background: #F8F9FA; }
        #customTitleBar { background: #E6EFEB; border-bottom: 1px solid #EAEAEA; }
        #customTitle { color: #183428; font-weight: 600; font-size: 15px; }
        #btnMin, #btnMax { background: transparent; border: none; color: #183428; font-size: 18px; }
        #btnClose { background: transparent; border: none; color: #B22222; font-size: 18px; }
        #btnMin:hover, #btnMax:hover { background: #D6E2DD; }
        #btnClose:hover { background: #F5B7B1; }
        #navFrame { background: #FFFFFF; border-right: 1px solid #EAEAEA; }
        #navTitle { font-weight: 700; font-size: 18px; padding: 6px; }
        QPushButton { border-radius: 6px; padding: 8px 12px; }
        QPlainTextEdit, QTextEdit { border: 1px solid #EAEAEA; border-radius: 8px; padding: 8px; }
        """

    def apply_theme(self, theme: Theme):
        bg = theme.color('background_color')
        surface = theme.color('surface_color')
        text = theme.color('text_color')
        primary = theme.color('primary_color')
        border = theme.color('border_color')
        accent = theme.color('accent_color')

        # calcular color de texto contrastante para el botón de enviar
        def hex_to_rgb(h: str):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def luminance(rgb):
            # fórmula relativa de luminancia aproximada
            r, g, b = [c/255.0 for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        try:
            prgb = hex_to_rgb(primary)
            send_text_color = '#000000' if luminance(prgb) > 0.65 else '#FFFFFF'
        except Exception:
            send_text_color = '#FFFFFF'

        sheet = f"""
        QMainWindow {{ background: {bg}; color: {text}; }}
        QFrame#customTitleBar {{ background: {surface}; border-bottom: 1px solid {border}; }}
        QLabel#customTitle {{ color: {primary}; font-weight: 600; font-size: 15px; }}
        #btnMin, #btnMax {{ background: transparent; border: none; color: {primary}; font-size: 18px; }}
        #btnClose {{ background: transparent; border: none; color: #B22222; font-size: 18px; }}
        #btnMin:hover, #btnMax:hover {{ background: {border}; }}
        #btnClose:hover {{ background: #F5B7B1; }}
        QFrame#navFrame {{ background: {surface}; border-right: 1px solid {border}; }}
        QLabel#navTitle {{ color: {primary}; font-weight: 700; font-size: 18px; }}
        QLabel#sectionLabel {{ color: {primary}; font-weight: 600; font-size: 13px; }}
        QPushButton {{ background: transparent; color: {text}; border: 1px solid {border}; border-radius: 6px; padding: 6px 10px; }}
        QPushButton:hover {{ background: {border}; }}
        QPushButton#sendButton {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {primary}, stop:1 {primary}); color: {send_text_color}; font-weight: 700; }}
        QPushButton#sendButton:hover {{ border: 2px solid {accent}; }}
        QPushButton#sendButton:pressed {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {accent}, stop:1 {primary}); }}
        QPlainTextEdit, QTextEdit {{ background: {surface}; color: {text}; border: 1px solid {border}; border-radius: 8px; padding: 8px; }}
        QListWidget {{ background: {surface}; color: {text}; border: 1px solid {border}; border-radius: 8px; padding: 6px; }}
        QComboBox {{ background: {surface}; color: {text}; border: 1px solid {border}; border-radius: 6px; padding: 4px; }}
        """
        self.setStyleSheet(sheet)

        # Update cycle button label to show current theme (friendly name)
        if self.current_theme_key:
            label = self.friendly_theme_label(self.current_theme_key, theme)
            self.btn_cycle_theme.setText(f"Tema: {label}")

    def friendly_theme_label(self, key: str, theme: Theme) -> str:
        """Devuelve una etiqueta corta y amigable para el tema (Dark/Light) si se puede inferir.

        Reglas:
        - Si el nombre del archivo/clave contiene 'dark' -> 'Dark'
        - Si contiene 'light' -> 'Light'
        - Si el JSON contiene 'theme_name' -> se usa ese valor
        - Si no, se devuelve la clave tal cual
        """
        if not key:
            return theme.display_name() or ''
        k = key.lower()
        if 'dark' in k:
            return 'Dark'
        if 'light' in k:
            return 'Light'
        # fallback to human name in JSON
        name = theme.display_name()
        if name:
            return name
        return key

    # Signal handlers (only UI behavior)
    def on_theme_change(self, name):
        t = self.themes.get(name)
        if t:
            self.apply_theme(t)

    def cycle_theme(self):
        if not self.theme_keys:
            return
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_keys)
        self.current_theme_key = self.theme_keys[self.current_theme_index]
        self.current_theme = self.themes.get(self.current_theme_key)
        if self.current_theme:
            self.apply_theme(self.current_theme)

    def on_config_saved(self, data: dict):
        """Manejador llamado cuando WelcomeDialog guarda la config.

        Actualiza el estado interno y, si es necesario, muestra confirmación.
        """
        try:
            self.config = data or {}
            self.configured = bool(self.config.get('phone_number') and self.config.get('id') and self.config.get('token'))
            # si la ventana principal tuviera campos para mostrar la config, actualizarlos
            if hasattr(self, 'input_phone'):
                try:
                    self.input_phone.setText(self.config.get('phone_number', ''))
                except Exception:
                    pass
            if hasattr(self, 'input_id'):
                try:
                    self.input_id.setText(self.config.get('id', ''))
                except Exception:
                    pass
            if hasattr(self, 'input_token'):
                try:
                    self.input_token.setText(self.config.get('token', ''))
                except Exception:
                    pass
        except Exception:
            pass

    def on_send_clicked(self):
        msg = self.txt_message.toPlainText().strip()
        nums_text = self.txt_numbers.toPlainText().strip()
        if not msg:
            self.append_status('ERROR: El mensaje está vacío.')
            return
        if not nums_text:
            self.append_status('ERROR: No hay números.')
            return
        numbers = [l.strip() for l in nums_text.splitlines() if l.strip()]
        # Normalize phone numbers: remove spaces, '+' and non-digit characters
        numbers = [normalize_phone(n) for n in numbers if normalize_phone(n)]
        if not numbers:
            self.append_status('ERROR: No hay números válidos.')
            return

        # Worker para enviar en background y no bloquear la UI
        from PyQt6 import QtCore as _QtCore
        from core.ultramsg import UltraMsgClient

        class SendWorker(_QtCore.QThread):
            result = _QtCore.pyqtSignal(str)

            def __init__(self, numbers, message, parent=None):
                super().__init__(parent)
                self.numbers = numbers
                self.message = message
                self._stopped = False

            def run(self):
                client = UltraMsgClient()
                if not client._validate():
                    self.result.emit('ERROR: credenciales faltantes en config.json')
                    return
                for to in self.numbers:
                    if self._stopped:
                        break
                    try:
                        resp = client.send_text(to, self.message)
                        if isinstance(resp, dict) and resp.get('error'):
                            self.result.emit(f'ERROR a {to}: {resp.get("error")} - {resp.get("detail", "")}')
                        else:
                            self.result.emit(f'OK a {to}: {resp}')
                    except Exception as e:
                        self.result.emit(f'ERROR a {to}: {e}')

            def stop(self):
                self._stopped = True

        self.append_status('Iniciando envíos...')
        self._send_worker = SendWorker(numbers, msg, parent=self)
        self._send_worker.result.connect(self.append_status)
        self._send_worker.start()

    def append_status(self, text: str):
        import datetime
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item = QtWidgets.QListWidgetItem(f'[{now}] {text}')
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.status_list.addItem(item)
        self.status_list.scrollToBottom()
        # Además, guardar en history.txt (append)
        try:
            hist_path = os.path.abspath(resource_path('..', 'database', 'history.txt'))
            os.makedirs(os.path.dirname(hist_path), exist_ok=True)
            with open(hist_path, 'a', encoding='utf-8') as hf:
                hf.write(f'[{now}] {text}\n')
        except Exception:
            pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
