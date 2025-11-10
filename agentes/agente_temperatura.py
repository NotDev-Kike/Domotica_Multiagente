# agentes/agente_temperatura.py - Agente optimizado para respuesta rápida
from .agente_base import AgenteBase
from datos_compartidos.estado_sistema import estado_sistema
from configuracion import CONFIG_AGENTES
import random
import time

class AgenteTemperatura(AgenteBase):
    def __init__(self, bus_mensajes, evento_parada):
        super().__init__('temperatura', bus_mensajes, evento_parada)
        self.config = CONFIG_AGENTES['temperatura']
        self.ultimo_ajuste = time.time()
    
    def ejecutar(self):
        while not self.evento_parada.is_set():
            try:
                # Obtener estado actual
                estado = estado_sistema.obtener_todo()
                temperatura_actual = estado['temperatura']
                calefaccion_activa = estado['calefaccion_activada']
                ventilador_activo = estado['ventilador_activado']
                
                # Aplicar variación natural de temperatura (más frecuente pero menor)
                variacion = random.uniform(*self.config['variacion_temperatura'])
                nueva_temperatura = temperatura_actual + variacion
                estado_sistema.actualizar('temperatura', nueva_temperatura)
                
                # Lógica de control de temperatura (RESPUESTA RÁPIDA)
                self.controlar_temperatura(nueva_temperatura, calefaccion_activa, ventilador_activo)
                
                # Procesar mensajes recibidos
                mensajes = self.recibir_mensajes()
                for mensaje in mensajes:
                    self.procesar_mensaje_temperatura(mensaje)
                
                # Aplicar efectos de los sistemas HVAC (actualización constante)
                self.aplicar_efectos_hvac()
                
                # Pausa optimizada
                self.dormir_seguro(0.3)  # 300ms en lugar de 1.5 segundos
                
            except Exception as error:
                print(f"[Agente Temperatura] Error: {error}")
                self.dormir_seguro(0.5)
    
    def controlar_temperatura(self, temperatura, calefaccion_activa, ventilador_activo):
        """Controla los sistemas de temperatura con respuesta inmediata"""
        # Temperatura muy baja -> activar calefacción inmediatamente
        if temperatura < self.config['temp_minima'] and not calefaccion_activa:
            estado_sistema.actualizar('calefaccion_activada', True)
            estado_sistema.registrar_evento("[Temperatura] Temperatura baja -> calefacción activada")
        
        # Temperatura muy alta -> activar ventilador inmediatamente  
        elif temperatura > self.config['temp_maxima'] and not ventilador_activo:
            estado_sistema.actualizar('ventilador_activado', True)
            estado_sistema.registrar_evento("[Temperatura] Temperatura alta -> ventilador activado")
        
        # Temperatura óptima -> desactivar sistemas
        elif (self.config['temp_optima_min'] <= temperatura <= self.config['temp_optima_max']):
            if calefaccion_activa:
                estado_sistema.actualizar('calefaccion_activada', False)
                estado_sistema.registrar_evento("[Temperatura] Temperatura óptima -> calefacción desactivada")
            
            if ventilador_activo:
                estado_sistema.actualizar('ventilador_activado', False)
                estado_sistema.registrar_evento("[Temperatura] Temperatura óptima -> ventilador desactivado")
    
    def procesar_mensaje_temperatura(self, mensaje):
        """Procesa mensajes relacionados con temperatura"""
        if (mensaje.get('objetivo') == 'temperatura' and 
            mensaje.get('tipo') == 'comando'):
            
            accion = mensaje.get('accion')
            if accion == 'activar_calefaccion':
                estado_sistema.actualizar('calefaccion_activada', True)
            elif accion == 'desactivar_calefaccion':
                estado_sistema.actualizar('calefaccion_activada', False)
            elif accion == 'activar_ventilador':
                estado_sistema.actualizar('ventilador_activado', True)
            elif accion == 'desactivar_ventilador':
                estado_sistema.actualizar('ventilador_activado', False)
            
            estado_sistema.registrar_evento(f"[Temperatura] Comando ejecutado: {accion}")
    
    def aplicar_efectos_hvac(self):
        """Aplica los efectos de calefacción y ventilación"""
        estado_actual = estado_sistema.obtener_todo()
        temperatura_actual = estado_actual['temperatura']
        
        if estado_actual['calefaccion_activada']:
            nueva_temp = temperatura_actual + self.config['potencia_calefaccion'] * 0.3
            estado_sistema.actualizar('temperatura', nueva_temp)
        
        if estado_actual['ventilador_activado']:
            nueva_temp = temperatura_actual - self.config['potencia_enfriamiento'] * 0.3
            estado_sistema.actualizar('temperatura', nueva_temp)