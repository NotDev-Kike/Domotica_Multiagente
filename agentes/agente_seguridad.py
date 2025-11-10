# agentes/agente_seguridad.py - Agente optimizado para respuesta inmediata al reset
from .agente_base import AgenteBase
from datos_compartidos.estado_sistema import estado_sistema
from configuracion import CONFIG_AGENTES
import random
import time

class AgenteSeguridad(AgenteBase):
    def __init__(self, bus_mensajes, evento_parada):
        super().__init__('seguridad', bus_mensajes, evento_parada)
        self.config = CONFIG_AGENTES['seguridad']
        self.ultima_alerta = 0
        self.tiempo_entre_alertas = 5  # Reducido a 5 segundos entre alertas
        self.reset_pendiente = False
    
    def inicializar(self):
        """Inicialización específica del agente de seguridad"""
        super().inicializar()
        print(f"[Seguridad] Configurado - Intervalo: {self.config['intervalo_verificacion']}s")
        print(f"[Seguridad] Tiempo entre alertas: {self.tiempo_entre_alertas}s")
    
    def ejecutar_ciclo(self):
        """Ciclo principal de ejecución - RESPUESTA MUY RÁPIDA"""
        try:
            # PRIMERO procesar mensajes (incluyendo reset) - ORDEN CRÍTICO
            mensajes = self.recibir_mensajes()
            if mensajes:
                for mensaje in mensajes:
                    self.procesar_mensaje_seguridad(mensaje)
            
            # LUEGO verificar movimiento (menos crítico)
            if random.random() < self.config['probabilidad_movimiento']:
                self.detectar_movimiento()
                
        except Exception as error:
            print(f"[Agente Seguridad] Error en ciclo: {error}")
            self.estadisticas['errores'] += 1
    
    def procesar_mensaje_seguridad(self, mensaje):
        """Procesa mensajes con RESPUESTA INMEDIATA para reset"""
        tipo_mensaje = mensaje.get('tipo')
        
        if tipo_mensaje == 'simular_movimiento':
            self.detectar_movimiento()
            estado_sistema.registrar_evento("[Seguridad] Movimiento simulado desde interfaz")
        
        elif tipo_mensaje == 'comando' and mensaje.get('objetivo') == 'seguridad':
            accion = mensaje.get('accion')
            if accion == 'reiniciar_alerta':
                # RESPUESTA INMEDIATA - sin verificación de tiempo
                estado_sistema.actualizar('alerta_seguridad', False)
                self.ultima_alerta = 0  # Resetear contador
                estado_sistema.registrar_evento("[Seguridad] Alerta reiniciada INMEDIATAMENTE")
                print(f"[Seguridad] Reset de alerta procesado inmediatamente")
        
        elif tipo_mensaje == 'movimiento':
            self.evaluar_movimiento(mensaje.get('valor'))
    
    def detectar_movimiento(self):
        """Detecta movimiento y activa las respuestas correspondientes"""
        # Enviar mensaje de movimiento con alta prioridad
        self.enviar_mensaje({
            'tipo': 'movimiento', 
            'valor': True,
            'prioridad': 'alta'
        })
        estado_sistema.registrar_evento("[Seguridad] Movimiento detectado")
        
        # Activar luces inmediatamente si es de noche
        if estado_sistema.obtener('es_noche'):
            self.enviar_mensaje({
                'tipo': 'comando', 
                'objetivo': 'iluminacion', 
                'accion': 'activar_luces',
                'prioridad': 'alta'
            })
    
    def evaluar_movimiento(self, hay_movimiento):
        """Evalúa si el movimiento representa una amenaza - CON RESET RÁPIDO"""
        if not hay_movimiento:
            return
        
        presencia_esperada = estado_sistema.obtener('presencia_esperada')
        tiempo_actual = time.time()
        
        # Solo activar alerta si no hay presencia esperada
        if not presencia_esperada:
            # Verificar si ha pasado el tiempo mínimo desde la última alerta
            if (tiempo_actual - self.ultima_alerta) > self.tiempo_entre_alertas:
                estado_sistema.actualizar('alerta_seguridad', True)
                self.ultima_alerta = tiempo_actual
                estado_sistema.registrar_evento("[Seguridad] ¡ALERTA! Movimiento sin presencia")
                
                # Activar luces inmediatamente
                self.enviar_mensaje({
                    'tipo': 'comando', 
                    'objetivo': 'iluminacion', 
                    'accion': 'activar_luces',
                    'prioridad': 'alta'
                })
    
    def finalizar(self):
        """Limpieza antes de terminar"""
        estado_sistema.actualizar('alerta_seguridad', False)  # Asegurar que la alerta se resetee
        super().finalizar()