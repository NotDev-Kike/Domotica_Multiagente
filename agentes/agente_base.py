# agentes/agente_base.py - Clase base optimizada para todos los agentes
import threading
import time

class AgenteBase(threading.Thread):
    def __init__(self, nombre, bus_mensajes, evento_parada):
        super().__init__(daemon=True)
        self.nombre = nombre
        self.bus_mensajes = bus_mensajes
        self.evento_parada = evento_parada
        self.ultimo_tiempo_procesamiento = time.time()
        self.estadisticas = {
            'ciclos_ejecutados': 0,
            'mensajes_enviados': 0,
            'mensajes_recibidos': 0,
            'errores': 0,
            'tiempo_total_ejecucion': 0.0
        }
    
    def enviar_mensaje(self, mensaje):
        """Envía un mensaje con prioridad para mensajes críticos"""
        try:
            mensaje = dict(mensaje)
            mensaje['de'] = self.nombre
            mensaje['marca_tiempo'] = time.time()
            
            # Prioridad para mensajes críticos (timeout más corto)
            if mensaje.get('tipo') in ['movimiento', 'alerta', 'comando_critico']:
                exito = self.bus_mensajes.enviar_mensaje(mensaje, tiempo_espera=0.02)
            else:
                exito = self.bus_mensajes.enviar_mensaje(mensaje, tiempo_espera=0.05)
            
            if exito:
                self.estadisticas['mensajes_enviados'] += 1
            return exito
            
        except Exception as error:
            print(f"[{self.nombre}] Error enviando mensaje: {error}")
            self.estadisticas['errores'] += 1
            return False
    
    def recibir_mensajes(self):
        """Recibe todos los mensajes disponibles con manejo de errores"""
        try:
            mensajes = self.bus_mensajes.recibir_todos_mensajes()
            self.estadisticas['mensajes_recibidos'] += len(mensajes)
            return mensajes
        except Exception as error:
            print(f"[{self.nombre}] Error recibiendo mensajes: {error}")
            self.estadisticas['errores'] += 1
            return []
    
    def dormir_seguro(self, duracion):
        """Pausa el agente verificando periódicamente si debe detenerse"""
        intervalo = 0.05  # Intervalo más corto para mejor respuesta
        tiempo_transcurrido = 0
        while tiempo_transcurrido < duracion and not self.evento_parada.is_set():
            time.sleep(intervalo)
            tiempo_transcurrido += intervalo
    
    def ejecutar_ciclo(self):
        """Ejecuta un ciclo del agente (debe ser implementado por subclases)"""
        raise NotImplementedError("Los agentes deben implementar el método ejecutar_ciclo")
    
    def inicializar(self):
        """Inicialización del agente (puede ser sobreescrito por subclases)"""
        print(f"[{self.nombre}] Agente inicializado")
    
    def finalizar(self):
        """Limpieza antes de terminar (puede ser sobreescrito por subclases)"""
        print(f"[{self.nombre}] Agente finalizado")
    
    def obtener_estadisticas(self):
        """Retorna las estadísticas del agente"""
        return self.estadisticas.copy()
    
    def ejecutar(self):
        """Bucle principal de ejecución del agente"""
        self.inicializar()
        tiempo_inicio = time.time()
        
        while not self.evento_parada.is_set():
            try:
                ciclo_inicio = time.time()
                
                # Ejecutar el ciclo principal del agente
                self.ejecutar_ciclo()
                
                # Actualizar estadísticas
                self.estadisticas['ciclos_ejecutados'] += 1
                ciclo_duracion = time.time() - ciclo_inicio
                self.estadisticas['tiempo_total_ejecucion'] += ciclo_duracion
                self.ultimo_tiempo_procesamiento = time.time()
                
                # Pequeña pausa para no saturar la CPU (puede ser ajustada por subclases)
                self.dormir_seguro(0.01)  # 10ms mínimos entre ciclos
                
            except Exception as error:
                print(f"[{self.nombre}] Error en ciclo de ejecución: {error}")
                self.estadisticas['errores'] += 1
                self.dormir_seguro(0.5)  # Pausa más larga en caso de error
        
        # Calcular tiempo total de ejecución
        tiempo_total = time.time() - tiempo_inicio
        self.estadisticas['tiempo_total_ejecucion'] = tiempo_total
        
        self.finalizar()
    
    def run(self):
        """Método principal del hilo (llama a ejecutar)"""
        self.ejecutar()
    
    def __str__(self):
        """Representación en string del agente"""
        stats = self.estadisticas
        return (f"Agente({self.nombre}) - "
                f"Ciclos: {stats['ciclos_ejecutados']}, "
                f"Msg Enviados: {stats['mensajes_enviados']}, "
                f"Msg Recibidos: {stats['mensajes_recibidos']}, "
                f"Errores: {stats['errores']}")
    
    def verificar_salud(self):
        """Verifica si el agente está funcionando correctamente"""
        tiempo_inactivo = time.time() - self.ultimo_tiempo_procesamiento
        return tiempo_inactivo < 5.0  # Considerado saludable si ha procesado en los últimos 5 segundos