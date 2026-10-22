"""Launcher para la UI de PandaMessage (solo diseño).

Ejecutar este archivo abre la ventana principal definida en `ui/main_window.py`.
Requiere PyQt6: `pip install PyQt6`.
"""

from PyQt6 import QtWidgets
import sys

try:
	from ui.main_window import MainWindow
except Exception as e:
	# Mostrar un mensaje de error sencillo si la importación falla
	print('Error al importar la interfaz:', e)
	raise


def main():
	print('Iniciando PandaMessage UI...')
	app = QtWidgets.QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec())


if __name__ == '__main__':
	main()
