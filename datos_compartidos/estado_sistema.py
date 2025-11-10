# datos_compartidos/estado_sistema.py - Estado compartido del sistema
import threading
import time

class EstadoSistema:
    def __init__(self):
        self._bloqueo = threading.Lock()
        self._estado = {
            'es_noche': False,
            'presencia_esperada': True,
            'movimiento_detectado': False,
            'temperatura': 22.0,
            'calefaccion_activada': False,
            'ventilador_activado': False,
            'luces_activadas': False,
            'alerta_seguridad': False,
            'registro_eventos': []
        }
    
    def actualizar(self, clave, valor):
        with self._bloqueo:
            self._estado[clave] = valor
    
    def obtener(self, clave):
        with self._bloqueo:
            return self._estado[clave]
    
    def obtener_todo(self):
        with self._bloqueo:
            return self._estado.copy()
    
    def registrar_evento(self, mensaje):
        with self._bloqueo:
            timestamp = time.strftime('%H:%M:%S')
            self._estado['registro_eventos'].insert(0, f"{timestamp} - {mensaje}")
            if len(self._estado['registro_eventos']) > 10:
                self._estado['registro_eventos'] = self._estado['registro_eventos'][:10]
    
    def limpiar_registro(self):
        with self._bloqueo:
            self._estado['registro_eventos'] = []

# Instancia global del estado del sistema
estado_sistema = EstadoSistema()