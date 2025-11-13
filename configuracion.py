# configuracion.py - Configuración optimizada para respuesta inmediata

# Configuración de la ventana
ANCHO_VENTANA = 1000
ALTO_VENTANA = 850
FPS = 60

# Configuración de agentes OPTIMIZADA PARA RESPUESTA INMEDIATA
CONFIG_AGENTES = {
    'temperatura': {
        'temp_minima': 19.5,
        'temp_maxima': 26.0,
        'temp_optima_min': 20.5,
        'temp_optima_max': 24.0,
        'potencia_calefaccion': 0.08,
        'potencia_enfriamiento': 0.10,
        'variacion_temperatura': (-0.05, 0.05)
    },
    'seguridad': {
        'probabilidad_movimiento': 0.01,
        'intervalo_verificacion': 0.02,  # MUCHO MÁS RÁPIDO: 50ms en lugar de 200ms
        'tiempo_entre_alertas': 5        # Reducido a 5 segundos
    },
    'iluminacion': {
        'intervalo_verificacion': 0.05,  # MUCHO MÁS RÁPIDO: 50ms
        'tiempo_encendido_automatico': 30
    }
}

# Comportamiento inteligente de iluminación
COMPORTAMIENTO_LUCES = {
    'encender_anochecer': True,
    'apagar_amanecer': True, 
    'mantener_noche_presencia': True,
    'encender_movimiento_noche': True
}

# TIEMPOS DE RESPUESTA MEJORADOS (MUCHO MÁS RÁPIDOS)
TIEMPOS_RESPUESTA = {
    'iluminacion': 0.05,    # 50ms (antes 100ms)
    'seguridad': 0.05,      # 50ms (antes 200ms)  
    'temperatura': 0.1,     # 100ms (antes 300ms)
    'interfaz': 0.016       # ~60 FPS
}

# Prioridades de mensajes
PRIORIDAD_MENSAJES = {
    'reset_alerta': 2,      # Máxima prioridad
    'comando': 2,           # Máxima prioridad  
    'movimiento': 1,        # Alta prioridad
    'alerta': 1,            # Alta prioridad
    'estado': 0,            # Prioridad normal
    'log': 0                # Prioridad normal
}

# Colores de la interfaz
COLORES = {
    'fondo_dia': (230, 235, 245),
    'fondo_noche': (25, 25, 45),
    'panel_principal': (250, 250, 250),
    'texto_principal': (20, 50, 100),
    'alerta': (200, 0, 0),
    'seguro': (0, 150, 0),
    'caliente': (200, 50, 50),
    'frio': (50, 50, 200),
    'optimo': (50, 150, 50),
    'activo': (0, 180, 0),
    'inactivo': (150, 150, 150),
    'luz_encendida': (255, 255, 100),
    'luz_apagada': (180, 180, 180)
}