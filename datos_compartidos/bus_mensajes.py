# datos_compartidos/bus_mensajes.py - Bus optimizado con prioridad para mensajes críticos
import queue
import threading
import time
import heapq

class MensajePriorizado:
    def __init__(self, mensaje, prioridad=0):
        self.mensaje = mensaje
        self.prioridad = prioridad  # 0=normal, 1=alta, 2=crítica
        self.timestamp = time.time()
    
    def __lt__(self, other):
        # Mensajes con mayor prioridad van primero
        if self.prioridad != other.prioridad:
            return self.prioridad > other.prioridad
        # Si misma prioridad, el más antiguo primero
        return self.timestamp < other.timestamp

class BusMensajes:
    def __init__(self, max_size=100):
        self._cola_priorizada = []  # Usamos heapq para cola priorizada
        self._lock = threading.Lock()
        self.estadisticas = {
            'mensajes_enviados': 0,
            'mensajes_recibidos': 0,
            'mensajes_perdidos': 0,
            'mensajes_alta_prioridad': 0
        }
    
    def enviar_mensaje(self, mensaje, tiempo_espera=0.05, prioridad=0):
        try:
            # Determinar prioridad automáticamente para mensajes críticos
            if mensaje.get('tipo') in ['comando', 'reiniciar_alerta']:
                prioridad = 2  # Máxima prioridad para comandos y reset
            elif mensaje.get('tipo') in ['movimiento', 'alerta']:
                prioridad = 1  # Alta prioridad para alertas
            
            mensaje_priorizado = MensajePriorizado(mensaje, prioridad)
            
            with self._lock:
                if len(self._cola_priorizada) >= 100:  # Límite máximo
                    # Remover mensajes más viejos con baja prioridad si es necesario
                    self._limpiar_mensajes_viejos()
                
                heapq.heappush(self._cola_priorizada, mensaje_priorizado)
                self.estadisticas['mensajes_enviados'] += 1
                if prioridad > 0:
                    self.estadisticas['mensajes_alta_prioridad'] += 1
            
            return True
            
        except Exception as e:
            self.estadisticas['mensajes_perdidos'] += 1
            return False
    
    def recibir_mensaje(self, tiempo_espera=0.1):
        try:
            inicio = time.time()
            while time.time() - inicio < tiempo_espera:
                with self._lock:
                    if self._cola_priorizada:
                        mensaje_priorizado = heapq.heappop(self._cola_priorizada)
                        self.estadisticas['mensajes_recibidos'] += 1
                        return mensaje_priorizado.mensaje
                
                time.sleep(0.01)  # Pequeña pausa para no saturar
            return None
            
        except Exception as e:
            return None
    
    def recibir_todos_mensajes(self):
        mensajes = []
        try:
            with self._lock:
                while self._cola_priorizada:
                    mensaje_priorizado = heapq.heappop(self._cola_priorizada)
                    mensajes.append(mensaje_priorizado.mensaje)
                    self.estadisticas['mensajes_recibidos'] += 1
        except Exception as e:
            pass
        return mensajes
    
    def _limpiar_mensajes_viejos(self):
        """Limpia mensajes con más de 2 segundos de antigüedad y baja prioridad"""
        try:
            tiempo_actual = time.time()
            mensajes_temporales = []
            
            while self._cola_priorizada:
                mensaje_priorizado = heapq.heappop(self._cola_priorizada)
                # Mantener mensajes recientes o de alta prioridad
                if (tiempo_actual - mensaje_priorizado.timestamp < 2 or 
                    mensaje_priorizado.prioridad > 0):
                    mensajes_temporales.append(mensaje_priorizado)
            
            # Reinsertar mensajes que se mantienen
            for mensaje in mensajes_temporales:
                heapq.heappush(self._cola_priorizada, mensaje)
                
        except Exception:
            pass
    
    def limpiar_cola(self):
        with self._lock:
            self._cola_priorizada = []
    
    def esta_vacia(self):
        with self._lock:
            return len(self._cola_priorizada) == 0
    
    def obtener_estadisticas(self):
        with self._lock:
            return self.estadisticas.copy()

# Instancia global del bus de mensajes
bus_mensajes = BusMensajes()