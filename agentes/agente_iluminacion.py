# agentes/agente_iluminacion.py - Agente optimizado usando la nueva clase base
from .agente_base import AgenteBase
from datos_compartidos.estado_sistema import estado_sistema
from configuracion import CONFIG_AGENTES, COMPORTAMIENTO_LUCES
import time

class AgenteIluminacion(AgenteBase):
    def __init__(self, bus_mensajes, evento_parada):
        super().__init__('iluminacion', bus_mensajes, evento_parada)
        self.config = CONFIG_AGENTES['iluminacion']
        self.comportamiento = COMPORTAMIENTO_LUCES
        self.ultimo_movimiento = 0
        self.ultimo_estado_noche = estado_sistema.obtener('es_noche')
    
    def inicializar(self):
        """Inicialización específica del agente de iluminación"""
        super().inicializar()
        print(f"[Iluminación] Configurado - Intervalo: {self.config['intervalo_verificacion']}s")
        print(f"[Iluminación] Comportamiento - Encender al anochecer: {self.comportamiento['encender_anochecer']}")
    
    def ejecutar_ciclo(self):
        """Ciclo principal de ejecución del agente de iluminación"""
        # Verificar cambio a noche para encender luces automáticamente
        self.verificar_cambio_a_noche()
        
        # Procesar mensajes recibidos
        mensajes = self.recibir_mensajes()
        for mensaje in mensajes:
            self.procesar_mensaje(mensaje)
        
        # Verificar condiciones para apagar luces automáticamente
        self.verificar_apagado_automatico()
    
    def verificar_cambio_a_noche(self):
        """Verifica si cambió a noche y enciende las luces automáticamente si hay presencia"""
        es_noche_actual = estado_sistema.obtener('es_noche')
        presencia_esperada = estado_sistema.obtener('presencia_esperada')
        luces_activadas = estado_sistema.obtener('luces_activadas')
        
        # Si acaba de cambiar a noche y hay presencia esperada, encender luces
        if (self.comportamiento['encender_anochecer'] and
            es_noche_actual and 
            not self.ultimo_estado_noche and 
            presencia_esperada and 
            not luces_activadas):
            
            estado_sistema.actualizar('luces_activadas', True)
            estado_sistema.registrar_evento("[Iluminación] Anochecer detectado -> luces encendidas automáticamente")
        
        # Actualizar el último estado de noche
        self.ultimo_estado_noche = es_noche_actual
    
    def procesar_mensaje(self, mensaje):
        """Procesa mensajes recibidos por el agente"""
        if mensaje.get('tipo') == 'movimiento':
            if self.comportamiento['encender_movimiento_noche']:
                es_noche = estado_sistema.obtener('es_noche')
                if es_noche:
                    self.encender_luces_automaticamente()
                    estado_sistema.registrar_evento("[Iluminación] Movimiento detectado en noche -> luces encendidas")
        
        elif (mensaje.get('tipo') == 'comando' and 
              mensaje.get('objetivo') == 'iluminacion'):
            
            accion = mensaje.get('accion')
            if accion == 'activar_luces':
                estado_sistema.actualizar('luces_activadas', True)
                estado_sistema.registrar_evento("[Iluminación] Luces activadas por comando")
            elif accion == 'desactivar_luces':
                estado_sistema.actualizar('luces_activadas', False)
                estado_sistema.registrar_evento("[Iluminación] Luces desactivadas por comando")
    
    def encender_luces_automaticamente(self):
        """Enciende las luces y registra el tiempo"""
        estado_sistema.actualizar('luces_activadas', True)
        self.ultimo_movimiento = time.time()
    
    def verificar_apagado_automatico(self):
        """Verifica si debe apagar las luces automáticamente"""
        estado_actual = estado_sistema.obtener_todo()
        
        # NO apagar automáticamente si es de noche y hay presencia esperada (comportamiento mejorado)
        if (self.comportamiento['mantener_noche_presencia'] and
            estado_actual['es_noche'] and 
            estado_actual['presencia_esperada']):
            return  # Mantener luces encendidas durante la noche con presencia
        
        # Condición 1: Sin presencia esperada y luces encendidas
        if (not estado_actual['presencia_esperada'] and 
            estado_actual['luces_activadas']):
            
            # Condición 2: Han pasado más de X segundos desde el último movimiento
            tiempo_actual = time.time()
            if (tiempo_actual - self.ultimo_movimiento) > self.config['tiempo_encendido_automatico']:
                estado_sistema.actualizar('luces_activadas', False)
                estado_sistema.registrar_evento("[Iluminación] Apagado automático por inactividad")
        
        # Condición 3: Es de día y las luces están encendidas (solo si no hay presencia)
        elif (self.comportamiento['apagar_amanecer'] and
              not estado_actual['es_noche'] and 
              estado_actual['luces_activadas'] and
              not estado_actual['presencia_esperada']):
            
            estado_sistema.actualizar('luces_activadas', False)
            estado_sistema.registrar_evento("[Iluminación] Apagado automático - Es de día")