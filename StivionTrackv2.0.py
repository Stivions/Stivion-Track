import sys
import json
import requests
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QMessageBox, QHBoxLayout, QStackedWidget, QFrame
)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt
import subprocess


class StivionGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stivion - Tracker")
        self.setMinimumSize(800, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: white;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                background-color: #2c2c3c;
                color: white;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #3e8e41;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #36a852;
            }
        """)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("🧭 Stivion - Herramientas de Rastreo")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        main_layout.addWidget(title)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_ip_tracker = QPushButton("🌐 Rastreo IP")
        self.btn_show_ip = QPushButton("🌍 Mostrar mi IP")
        self.btn_phone_tracker = QPushButton("📱 Rastreo Teléfono")
        self.btn_username_tracker = QPushButton("👤 Rastreo Usuario")

        for btn in [self.btn_ip_tracker, self.btn_show_ip, self.btn_phone_tracker, self.btn_username_tracker]:
            btn.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(self.btn_ip_tracker)
        btn_layout.addWidget(self.btn_show_ip)
        btn_layout.addWidget(self.btn_phone_tracker)
        btn_layout.addWidget(self.btn_username_tracker)

        main_layout.addLayout(btn_layout)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.screen_ip_tracker = self.ip_tracker_screen()
        self.screen_show_ip = self.show_ip_screen()
        self.screen_phone_tracker = self.phone_tracker_screen()
        self.screen_username_tracker = self.username_tracker_screen()

        self.stack.addWidget(self.screen_ip_tracker)
        self.stack.addWidget(self.screen_show_ip)
        self.stack.addWidget(self.screen_phone_tracker)
        self.stack.addWidget(self.screen_username_tracker)

        self.btn_ip_tracker.clicked.connect(lambda: self.stack.setCurrentWidget(self.screen_ip_tracker))
        self.btn_show_ip.clicked.connect(lambda: self.stack.setCurrentWidget(self.screen_show_ip))
        self.btn_phone_tracker.clicked.connect(lambda: self.stack.setCurrentWidget(self.screen_phone_tracker))
        self.btn_username_tracker.clicked.connect(lambda: self.stack.setCurrentWidget(self.screen_username_tracker))

        self.setLayout(main_layout)

    def ip_tracker_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Ingrese la dirección IP a rastrear:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Ejemplo: 8.8.8.8")

        self.ip_result = QTextEdit()
        self.ip_result.setReadOnly(True)
        self.ip_result.setFontFamily("Courier New")

        btn_track = QPushButton("🔍 Rastrear IP")
        btn_track.clicked.connect(self.ip_track_func)

        layout.addWidget(label)
        layout.addWidget(self.ip_input)
        layout.addWidget(btn_track)
        layout.addWidget(self.ip_result)

        widget.setLayout(layout)
        return widget

    def ip_track_func(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Error", "Por favor, ingrese una dirección IP válida.")
            return
        self.ip_result.clear()
        try:
            url = f"http://ipwho.is/{ip}"
            res = requests.get(url, timeout=10)
            data = res.json()

            if not data['success']:
                self.ip_result.setText(f"No se pudo obtener información para la IP: {ip}")
                return

            info = (
                f"Información de la IP: {ip}\n"
                f"Tipo: {data.get('type')}\n"
                f"País: {data.get('country')} ({data.get('country_code')})\n"
                f"Ciudad: {data.get('city')}\n"
                f"Continente: {data.get('continent')} ({data.get('continent_code')})\n"
                f"Región: {data.get('region')} ({data.get('region_code')})\n"
                f"Latitud: {data.get('latitude')}\n"
                f"Longitud: {data.get('longitude')}\n"
                f"Mapa: https://www.google.com/maps/@{data.get('latitude')},{data.get('longitude')},8z\n"
                f"EU: {data.get('is_eu')}\n"
                f"Código postal: {data.get('postal')}\n"
                f"Código de llamada: {data.get('calling_code')}\n"
                f"Capital: {data.get('capital')}\n"
                f"Bordes: {data.get('borders')}\n"
                f"Bandera: {data.get('flag', {}).get('emoji')}\n"
                f"ASN: {data.get('connection', {}).get('asn')}\n"
                f"ORG: {data.get('connection', {}).get('org')}\n"
                f"ISP: {data.get('connection', {}).get('isp')}\n"
                f"Dominio: {data.get('connection', {}).get('domain')}\n"
                f"Zona horaria ID: {data.get('timezone', {}).get('id')}\n"
                f"Abreviación: {data.get('timezone', {}).get('abbr')}\n"
                f"DST: {data.get('timezone', {}).get('is_dst')}\n"
                f"Offset: {data.get('timezone', {}).get('offset')}\n"
                f"UTC: {data.get('timezone', {}).get('utc')}\n"
                f"Hora actual: {data.get('timezone', {}).get('current_time')}\n"
            )
            self.ip_result.setText(info)
        except Exception as e:
            self.ip_result.setText(f"Error al obtener datos: {str(e)}")

    def show_ip_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Mostrar tu dirección IP pública:")
        self.show_ip_result = QTextEdit()
        self.show_ip_result.setReadOnly(True)
        self.show_ip_result.setFontFamily("Courier New")

        btn_show = QPushButton("🌐 Mostrar IP")
        btn_show.clicked.connect(self.show_my_ip_func)

        layout.addWidget(label)
        layout.addWidget(btn_show)
        layout.addWidget(self.show_ip_result)

        widget.setLayout(layout)
        return widget

    def show_my_ip_func(self):
        self.show_ip_result.clear()
        try:
            res = requests.get('https://api.ipify.org/', timeout=5)
            ip = res.text
            self.show_ip_result.setText(f"Tu dirección IP pública es: {ip}")
        except Exception as e:
            self.show_ip_result.setText(f"Error al obtener IP: {str(e)}")

    def phone_tracker_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Ingrese el número de teléfono a rastrear (con código de país):")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Ejemplo: +521234567890")

        self.phone_result = QTextEdit()
        self.phone_result.setReadOnly(True)
        self.phone_result.setFontFamily("Courier New")

        btn_track = QPushButton("📞 Rastrear teléfono")
        btn_track.clicked.connect(self.phone_track_func)

        layout.addWidget(label)
        layout.addWidget(self.phone_input)
        layout.addWidget(btn_track)
        layout.addWidget(self.phone_result)

        widget.setLayout(layout)
        return widget

    def phone_track_func(self):
        phone = self.phone_input.text().strip()
        if not phone:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un número de teléfono válido.")
            return
        self.phone_result.clear()
        try:
            default_region = "ID"

            parsed_number = phonenumbers.parse(phone, default_region)
            region_code = phonenumbers.region_code_for_number(parsed_number)
            provider = carrier.name_for_number(parsed_number, "es")
            location = geocoder.description_for_number(parsed_number, "es")
            is_valid = phonenumbers.is_valid_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            formatted_intl = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            formatted_mobile = phonenumbers.format_number_for_mobile_dialing(parsed_number, default_region, with_formatting=True)
            number_type = phonenumbers.number_type(parsed_number)
            timezones = timezone.time_zones_for_number(parsed_number)
            tz_str = ', '.join(timezones)

            tipo = "Otro tipo de número"
            if number_type == phonenumbers.PhoneNumberType.MOBILE:
                tipo = "Número móvil"
            elif number_type == phonenumbers.PhoneNumberType.FIXED_LINE:
                tipo = "Número fijo"

            info = (
                f"Información del número: {phone}\n"
                f"Ubicación: {location}\n"
                f"Código de región: {region_code}\n"
                f"Zona horaria: {tz_str}\n"
                f"Operador: {provider}\n"
                f"Número válido: {is_valid}\n"
                f"Número posible: {is_possible}\n"
                f"Formato internacional: {formatted_intl}\n"
                f"Formato móvil: {formatted_mobile}\n"
                f"Número original: {parsed_number.national_number}\n"
                f"Formato E.164: {phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)}\n"
                f"Código país: {parsed_number.country_code}\n"
                f"Número local: {parsed_number.national_number}\n"
                f"Tipo: {tipo}\n"
            )
            self.phone_result.setText(info)
        except Exception as e:
            self.phone_result.setText(f"Error al procesar el número: {str(e)}")

    def username_tracker_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)

        label = QLabel("Ingrese el nombre de usuario a rastrear:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ejemplo: stivion")

        self.username_result = QTextEdit()
        self.username_result.setReadOnly(True)
        self.username_result.setFontFamily("Courier New")

        btn_track = QPushButton("🔎 Rastrear usuario")
        btn_track.clicked.connect(self.username_track_func)

        layout.addWidget(label)
        layout.addWidget(self.username_input)
        layout.addWidget(btn_track)
        layout.addWidget(self.username_result)

        widget.setLayout(layout)
        return widget

    def username_track_func(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre de usuario válido.")
            return

        self.username_result.clear()
        try:
            resultado = subprocess.run(
                ['sherlock', username],
                capture_output=True,
                text=True,
                check=True
            )
            self.username_result.setText(resultado.stdout)
        except subprocess.CalledProcessError as e:
            self.username_result.setText(f"Error al ejecutar Sherlock:\n{e.stderr}")
        except FileNotFoundError:
            self.username_result.setText("Error: Sherlock no está instalado o no está en el PATH.")
        except Exception as e:
            self.username_result.setText(f"Error inesperado: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = StivionGUI()
    gui.show()
    sys.exit(app.exec())
