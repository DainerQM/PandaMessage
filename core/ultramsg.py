"""Cliente mínimo para interactuar con la API de UltraMsg.

Este cliente usa el esquema público de UltraMsg para enviar mensajes mediante
HTTP. Lee por defecto la configuración de `config.json` en la raíz del proyecto
si no se le pasan credenciales explícitas.

Notas:
- No incluye todas las rutas de la API, sólo lo necesario para enviar mensajes
  de texto y multimedia.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Optional, Dict, Any

import requests


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


class UltraMsgClient:
	def __init__(self, phone_number: Optional[str] = None, id: Optional[str] = None, token: Optional[str] = None, config_path: Optional[str] = None):
		# Use user-writable location for config file
		if config_path:
			self.config_path = config_path
		else:
			# First try to get from user config location
			self.config_path = get_user_config_path()
			
			# If config doesn't exist in user location, try to copy from installation
			if not os.path.exists(self.config_path):
				try:
					# Try to find config in installation directory (read-only)
					if hasattr(sys, '_MEIPASS'):
						install_config = os.path.join(sys._MEIPASS, 'config.json')
					else:
						install_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.json'))
					
					# Copy config from installation to user directory if it exists
					if os.path.exists(install_config):
						import shutil
						shutil.copy2(install_config, self.config_path)
				except Exception:
					pass  # If copying fails, we'll create a new config when needed
					
		self.phone_number = phone_number
		self.id = id
		self.token = token
		if not (self.phone_number and self.id and self.token):
			self._load_from_config()

		# tiempo por defecto
		self.timeout = 12

	def _load_from_config(self):
		try:
			if os.path.exists(self.config_path):
				with open(self.config_path, 'r', encoding='utf-8') as f:
					data = json.load(f)
				self.phone_number = self.phone_number or data.get('phone_number')
				self.id = self.id or data.get('id')
				self.token = self.token or data.get('token')
		except Exception:
			pass

	def _validate(self) -> bool:
		return bool(self.phone_number and self.id and self.token)

	def _base_url(self) -> str:
		# UltraMsg typical base: https://api.ultramsg.com/{instance_id}
		return f"https://api.ultramsg.com/{self.id}"

	def send_text(self, to: str, message: str) -> Dict[str, Any]:
		"""Enviar un mensaje de texto al número `to`.

		Args:
			to: número destino en formato internacional (ej: 521XXXXXXXXXX)
			message: texto a enviar

		Returns:
			dict: respuesta JSON de la API o diccionario con 'error'.
		"""
		if not self._validate():
			return {'error': 'missing_configuration'}

		url = f"{self._base_url()}/messages/chat"
		payload = {
			'token': self.token,
			'to': to,
			'body': message,
		}
		try:
			r = requests.post(url, json=payload, timeout=self.timeout)
			r.raise_for_status()
			return r.json()
		except requests.RequestException as e:
			return {'error': 'request_exception', 'detail': str(e)}

	def send_media(self, to: str, message: str, media_url: str, filename: Optional[str] = None) -> Dict[str, Any]:
		"""Enviar mensaje con media (por URL) usando endpoint de media si está disponible.

		Muchos proveedores aceptan un campo 'media' o 'file' — esto depende de la API.
		Ajusta según tu instancia de UltraMsg si el endpoint varía.
		"""
		if not self._validate():
			return {'error': 'missing_configuration'}

		url = f"{self._base_url()}/messages/media"
		payload = {
			'token': self.token,
			'to': to,
			'body': message,
			'media': media_url
		}
		if filename:
			payload['filename'] = filename
		try:
			r = requests.post(url, json=payload, timeout=self.timeout)
			r.raise_for_status()
			return r.json()
		except requests.RequestException as e:
			return {'error': 'request_exception', 'detail': str(e)}


if __name__ == '__main__':
	# Pequeña demo local (no ejecutar en producción con credenciales reales en hardcode)
	client = UltraMsgClient()
	if not client._validate():
		print('Faltan credenciales en config.json (phone_number, id, token).')
	else:
		resp = client.send_text(client.phone_number, 'Mensaje de prueba desde PandaMessage')
		print(resp)

