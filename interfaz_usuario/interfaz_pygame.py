# interfaz_usuario/interfaz_pygame.py - Interfaz gráfica del sistema
import pygame
from datos_compartidos.estado_sistema import estado_sistema
from datos_compartidos.bus_mensajes import bus_mensajes
from configuracion import ANCHO_VENTANA, ALTO_VENTANA, FPS, COLORES

class InterfazPygame:
    def __init__(self):
        self.ancho = ANCHO_VENTANA
        self.alto = ALTO_VENTANA
        self.fps = FPS
        self.pantalla = None
        self.reloj = None
        self.fuentes = {}
        self.estado_anterior = None
        self.contador_frames = 0
    
    def inicializar(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Sistema Domótica Multiagente")
        self.reloj = pygame.time.Clock()
        
        # Inicializar fuentes
        self.fuentes = {
            'titulo': pygame.font.SysFont("Arial", 32, bold=True),
            'seccion': pygame.font.SysFont("Arial", 24, bold=True),
            'normal': pygame.font.SysFont("Arial", 20),
            'pequena': pygame.font.SysFont("Arial", 16)
        }
    
    def dibujar_texto(self, x, y, texto, color=COLORES['texto_principal'], fuente='normal', centrado=False):
        fuente_obj = self.fuentes[fuente]
        superficie = fuente_obj.render(texto, True, color)
        if centrado:
            x = x - superficie.get_width() // 2
        self.pantalla.blit(superficie, (x, y))
        return superficie.get_width()
    
    def dibujar_seccion(self, x, y, ancho, alto, titulo, color_fondo=COLORES['panel_principal']):
        # Fondo de la sección
        pygame.draw.rect(self.pantalla, color_fondo, (x, y, ancho, alto), border_radius=8)
        pygame.draw.rect(self.pantalla, (180, 180, 180), (x, y, ancho, alto), 2, border_radius=8)
        
        # Título de la sección
        fondo_titulo = pygame.Rect(x, y-5, ancho, 30)
        pygame.draw.rect(self.pantalla, (200, 200, 220), fondo_titulo, border_radius=8)
        pygame.draw.rect(self.pantalla, (150, 150, 180), fondo_titulo, 1, border_radius=8)
        self.dibujar_texto(x + ancho//2, y, titulo, COLORES['texto_principal'], 'seccion', centrado=True)
        
        return y + 35
    
    def dibujar_vista_casa(self):
        # Panel izquierdo: Vista de la casa
        x_casa, y_casa = 20, 60
        ancho_casa, alto_casa = 460, 620
        
        y_contenido = self.dibujar_seccion(x_casa, y_casa, ancho_casa, alto_casa, "VISTA DE LA CASA", (250, 250, 255))
        
        # Habitaciones en grid 2x2
        tamano_habitacion = 180
        margen_habitaciones = 25
        x_inicio = x_casa + 40
        y_inicio = y_contenido + 20
        
        habitaciones = [
            (x_inicio, y_inicio, "SALA", (220, 240, 255), "Luces"),
            (x_inicio + tamano_habitacion + margen_habitaciones, y_inicio, "COCINA", (255, 240, 220), "Temperatura"),
            (x_inicio, y_inicio + tamano_habitacion + margen_habitaciones, "DORMITORIO", (255, 220, 240), "HVAC"),
            (x_inicio + tamano_habitacion + margen_habitaciones, y_inicio + tamano_habitacion + margen_habitaciones, "GARAGE", (220, 255, 230), "Seguridad")
        ]
        
        estado = estado_sistema.obtener_todo()
        
        for x, y, nombre, color, tipo in habitaciones:
            # Dibujar habitación
            pygame.draw.rect(self.pantalla, color, (x, y, tamano_habitacion, tamano_habitacion), border_radius=10)
            pygame.draw.rect(self.pantalla, (150, 150, 150), (x, y, tamano_habitacion, tamano_habitacion), 2, border_radius=10)
            
            # Nombre de la habitación
            self.dibujar_texto(x + tamano_habitacion//2, y + 15, nombre, (50, 50, 50), 'seccion', centrado=True)
            
            # Contenido específico
            if tipo == "Luces":
                color_luz = (255, 255, 100) if estado['luces_activadas'] else (180, 180, 180)
                pygame.draw.circle(self.pantalla, color_luz, (x + tamano_habitacion//2, y + 70), 25)
                pygame.draw.circle(self.pantalla, (100, 100, 100), (x + tamano_habitacion//2, y + 70), 25, 2)
                estado_luces = "ACTIVADAS" if estado['luces_activadas'] else "DESACTIVADAS"
                self.dibujar_texto(x + tamano_habitacion//2, y + 110, f"Luces: {estado_luces}", (40, 40, 40), 'pequena', centrado=True)
                
            elif tipo == "Temperatura":
                temp = estado['temperatura']
                color_temp = COLORES['caliente'] if temp > 24 else COLORES['frio'] if temp < 20 else COLORES['optimo']
                self.dibujar_texto(x + tamano_habitacion//2, y + 60, "Temperatura", (40, 40, 40), 'pequena', centrado=True)
                self.dibujar_texto(x + tamano_habitacion//2, y + 85, f"{temp:.1f} °C", color_temp, 'normal', centrado=True)
                
            elif tipo == "HVAC":
                self.dibujar_texto(x + tamano_habitacion//2, y + 60, "Sistema HVAC", (40, 40, 40), 'pequena', centrado=True)
                self.dibujar_texto(x + 20, y + 90, f"Calefacción: {'● ON' if estado['calefaccion_activada'] else '○ OFF'}", 
                                 COLORES['caliente'] if estado['calefaccion_activada'] else (100, 100, 100), 'pequena')
                self.dibujar_texto(x + 20, y + 115, f"Ventilador: {'● ON' if estado['ventilador_activado'] else '○ OFF'}", 
                                 COLORES['frio'] if estado['ventilador_activado'] else (100, 100, 100), 'pequena')
                
            elif tipo == "Seguridad":
                color_seguridad = COLORES['alerta'] if estado['alerta_seguridad'] else COLORES['seguro']
                estado_seguridad = "ALERTA!" if estado['alerta_seguridad'] else "SEGURO"
                pygame.draw.rect(self.pantalla, color_seguridad, (x + 20, y + 70, tamano_habitacion - 40, 50), border_radius=8)
                self.dibujar_texto(x + tamano_habitacion//2, y + 85, estado_seguridad, (255, 255, 255), 'normal', centrado=True)
        
        # Estado general
        y_general = y_inicio + 2 * (tamano_habitacion + margen_habitaciones) + 30
        y_contenido_general = self.dibujar_seccion(x_casa + 40, y_general, ancho_casa - 80, 120, "ESTADO GENERAL")
        
        self.dibujar_texto(x_casa + 60, y_contenido_general, 
                          f"● Presencia: {'ESPERADA' if estado['presencia_esperada'] else 'NO ESPERADA'}", 
                          COLORES['seguro'] if estado['presencia_esperada'] else COLORES['alerta'], 'pequena')
        self.dibujar_texto(x_casa + 60, y_contenido_general + 25, 
                          f"● Momento: {'NOCHE' if estado['es_noche'] else 'DÍA'}", 
                          (40, 40, 40), 'pequena')
        self.dibujar_texto(x_casa + 60, y_contenido_general + 50, 
                          f"● Modo: {'AUTOMÁTICO' if estado['presencia_esperada'] else 'AUSENTE'}", 
                          (60, 60, 150), 'pequena')
    
    def dibujar_panel_control(self):
        # Panel derecho: Controles y registros
        x_panel = 500
        ancho_panel = 480
        
        # Sección de controles
        y_controles = self.dibujar_seccion(x_panel, 60, ancho_panel, 280, "CONTROLES DEL SISTEMA", (255, 250, 240))
        
        self.dibujar_texto(x_panel + 20, y_controles, "Usa las siguientes teclas:", (60, 60, 60), 'pequena')
        
        controles = [
            ("P", "Alternar presencia esperada"),
            ("M", "Simular movimiento (sensor PIR)"),
            ("N", "Alternar entre día y noche"),
            ("T", "Aumentar temperatura (+1°C)"),
            ("G", "Disminuir temperatura (-1°C)"),
            ("R", "Resetear alerta de seguridad"),
            ("ESC", "Salir del sistema")
        ]
        
        for i, (tecla, descripcion) in enumerate(controles):
            y_pos = y_controles + 35 + i * 30
            if i % 2 == 0:
                pygame.draw.rect(self.pantalla, (245, 248, 255), (x_panel + 15, y_pos - 5, ancho_panel - 30, 25), border_radius=5)
            
            self.dibujar_texto(x_panel + 30, y_pos, f"{tecla}:", (0, 80, 160), 'pequena')
            self.dibujar_texto(x_panel + 80, y_pos, descripcion, (40, 40, 40), 'pequena')
        
        # Sección de estado actual
        y_estado = 60 + 300
        y_contenido_estado = self.dibujar_seccion(x_panel, y_estado, ancho_panel, 180, "ESTADO ACTUAL DEL SISTEMA", (240, 255, 240))
        
        estado = estado_sistema.obtener_todo()
        info_estado = [
            f"Temperatura: {estado['temperatura']:.1f} °C",
            f"Luces: {'ACTIVADAS' if estado['luces_activadas'] else 'DESACTIVADAS'}",
            f"Calefacción: {'ACTIVA' if estado['calefaccion_activada'] else 'INACTIVA'}",
            f"Ventilador: {'ACTIVO' if estado['ventilador_activado'] else 'INACTIVO'}",
            f"Alerta Seguridad: {'ACTIVA' if estado['alerta_seguridad'] else 'INACTIVA'}",
            f"Presencia: {'ESPERADA' if estado['presencia_esperada'] else 'NO ESPERADA'}"
        ]
        
        for i, texto in enumerate(info_estado):
            y_pos = y_contenido_estado + i * 25
            color = (50, 50, 50)
            if "ACTIVA" in texto or "ACTIVADAS" in texto or "ESPERADA" in texto:
                color = COLORES['seguro']
            elif "INACTIVA" in texto or "DESACTIVADAS" in texto or "NO ESPERADA" in texto:
                color = COLORES['alerta']
            elif "Temperatura" in texto:
                temp = estado['temperatura']
                if temp > 24:
                    color = COLORES['caliente']
                elif temp < 20:
                    color = COLORES['frio']
                else:
                    color = COLORES['optimo']
                    
            self.dibujar_texto(x_panel + 30, y_pos, f"● {texto}", color, 'pequena')
        
        # Sección de registro de eventos
        y_registro = y_estado + 200
        y_contenido_registro = self.dibujar_seccion(x_panel, y_registro, ancho_panel, 240, "REGISTRO DE EVENTOS DEL SISTEMA", (240, 240, 250))
        
        eventos = estado_sistema.obtener('registro_eventos')
        
        pygame.draw.rect(self.pantalla, (250, 250, 255), (x_panel + 15, y_contenido_registro, ancho_panel - 30, 190), border_radius=5)
        pygame.draw.rect(self.pantalla, (220, 220, 230), (x_panel + 15, y_contenido_registro, ancho_panel - 30, 190), 1, border_radius=5)
        
        for i, evento in enumerate(eventos[:8]):
            y_pos = y_contenido_registro + 5 + i * 22
            if i % 2 == 0:
                pygame.draw.rect(self.pantalla, (245, 248, 255), (x_panel + 20, y_pos, ancho_panel - 40, 20), border_radius=3)
            
            if "ALERTA" in evento or "ERROR" in evento:
                color = COLORES['alerta']
            elif "Temperatura" in evento:
                color = (0, 100, 200)
            elif "Iluminación" in evento:
                color = (200, 150, 0)
            elif "Seguridad" in evento:
                color = (150, 0, 150)
            else:
                color = (60, 60, 60)
                
            self.dibujar_texto(x_panel + 25, y_pos, evento, color, 'pequena')
    
    def ejecutar(self, evento_parada):
        self.inicializar()
        ejecutando = True
        
        while ejecutando and not evento_parada.is_set():
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                    evento_parada.set()
                elif evento.type == pygame.KEYDOWN:
                    self.manejar_teclado(evento.key, evento_parada)
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando = False
            
            # Verificar si el estado cambió para evitar redibujado innecesario
            estado_actual = estado_sistema.obtener_todo()
            claves_estado = (
                estado_actual['luces_activadas'],
                round(estado_actual['temperatura'], 1),
                estado_actual['calefaccion_activada'],
                estado_actual['ventilador_activado'],
                estado_actual['presencia_esperada'],
                estado_actual['es_noche'],
                estado_actual['alerta_seguridad']
            )
            
            self.contador_frames += 1
            if claves_estado != self.estado_anterior or self.contador_frames % 10 == 0:
                self.estado_anterior = claves_estado
                
                # Fondo principal según momento del día
                if estado_actual['es_noche']:
                    self.pantalla.fill(COLORES['fondo_noche'])
                else:
                    self.pantalla.fill(COLORES['fondo_dia'])
                
                # Título principal
                self.dibujar_texto(self.ancho//2, 15, "Sistema Domótica Multiagente", 
                                 COLORES['texto_principal'], 'titulo', centrado=True)
                
                # Dibujar componentes
                self.dibujar_vista_casa()
                self.dibujar_panel_control()
                
                pygame.display.flip()
            
            self.reloj.tick(self.fps)
        
        pygame.quit()

    def manejar_teclado(self, tecla, evento_parada):
        if tecla == pygame.K_p:
            estado_actual = estado_sistema.obtener('presencia_esperada')
            nuevo_estado = not estado_actual
            estado_sistema.actualizar('presencia_esperada', nuevo_estado)
            
            if nuevo_estado and estado_sistema.obtener('es_noche'):
                estado_sistema.actualizar('luces_activadas', True)
                estado_sistema.registrar_evento("[Interfaz] Presencia activada en noche -> luces encendidas")
            else:
                estado_sistema.registrar_evento(f"[Interfaz] Presencia: {'ACTIVADA' if nuevo_estado else 'DESACTIVADA'}")
        
        elif tecla == pygame.K_m:
            if bus_mensajes.enviar_mensaje(
                {'de': 'interfaz', 'tipo': 'simular_movimiento', 'valor': True}, 
                prioridad=1  # Alta prioridad
            ):
                estado_sistema.registrar_evento("[Interfaz] Movimiento simulado")
            else:
                estado_sistema.registrar_evento("[Interfaz] Error: Cola de mensajes llena")
        
        elif tecla == pygame.K_n:
            estado_actual = estado_sistema.obtener('es_noche')
            nuevo_estado = not estado_actual
            estado_sistema.actualizar('es_noche', nuevo_estado)
            
            presencia_esperada = estado_sistema.obtener('presencia_esperada')
            luces_activadas = estado_sistema.obtener('luces_activadas')
            
            if nuevo_estado:
                estado_sistema.registrar_evento("[Interfaz] Modo cambiado a NOCHE")
                if presencia_esperada and not luces_activadas:
                    estado_sistema.actualizar('luces_activadas', True)
                    estado_sistema.registrar_evento("[Interfaz] Anochecer con presencia -> luces encendidas")
            else:
                estado_sistema.registrar_evento("[Interfaz] Modo cambiado a DÍA")
                if not presencia_esperada and luces_activadas:
                    estado_sistema.actualizar('luces_activadas', False)
                    estado_sistema.registrar_evento("[Interfaz] Amanecer sin presencia -> luces apagadas")
        
        elif tecla == pygame.K_t:
            temperatura_actual = estado_sistema.obtener('temperatura')
            estado_sistema.actualizar('temperatura', min(35.0, temperatura_actual + 1.0))
            estado_sistema.registrar_evento("[Interfaz] Temperatura aumentada")
        
        elif tecla == pygame.K_g:
            temperatura_actual = estado_sistema.obtener('temperatura')
            estado_sistema.actualizar('temperatura', max(15.0, temperatura_actual - 1.0))
            estado_sistema.registrar_evento("[Interfaz] Temperatura disminuida")
        
        elif tecla == pygame.K_r:
            # RESET INMEDIATO - Enviar con máxima prioridad
            if bus_mensajes.enviar_mensaje({
                'de': 'interfaz', 
                'tipo': 'comando', 
                'objetivo': 'seguridad', 
                'accion': 'reiniciar_alerta'
            }, prioridad=2):  # Prioridad máxima
                # También actualizar el estado localmente para respuesta inmediata
                estado_sistema.actualizar('alerta_seguridad', False)
                estado_sistema.registrar_evento("[Interfaz] Alerta reiniciada INMEDIATAMENTE")
                print("[Interfaz] Reset de alerta enviado con prioridad máxima")
            else:
                estado_sistema.registrar_evento("[Interfaz] Error: No se pudo enviar reset")