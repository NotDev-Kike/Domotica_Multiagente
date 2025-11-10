# ejecutar_sistema.py - Archivo principal para ejecutar el sistema
import threading
import time
from agentes.agente_temperatura import AgenteTemperatura
from agentes.agente_iluminacion import AgenteIluminacion
from agentes.agente_seguridad import AgenteSeguridad
from interfaz_usuario.interfaz_pygame import InterfazPygame
from datos_compartidos.bus_mensajes import bus_mensajes
from datos_compartidos.estado_sistema import estado_sistema

def main():
    print("🚀 Iniciando Sistema Domótica Multiagente...")
    
    # Crear evento de parada global
    evento_parada = threading.Event()
    
    # Crear agentes
    agentes = [
        AgenteTemperatura(bus_mensajes, evento_parada),
        AgenteIluminacion(bus_mensajes, evento_parada),
        AgenteSeguridad(bus_mensajes, evento_parada)
    ]
    
    # Iniciar agentes
    for agente in agentes:
        agente.start()
        estado_sistema.registrar_evento(f"[Sistema] Agente {agente.nombre} iniciado")
        print(f"✅ Agente {agente.nombre} iniciado")
    
    try:
        # Iniciar interfaz de usuario
        interfaz = InterfazPygame()
        interfaz.ejecutar(evento_parada)
        
    except Exception as error:
        print(f"❌ Error en la interfaz: {error}")
        estado_sistema.registrar_evento(f"[Sistema] Error crítico: {error}")
    
    finally:
        print("🛑 Cerrando sistema...")
        evento_parada.set()
        
        # Dar tiempo a los agentes para cerrar
        time.sleep(1)
        
        # Limpiar la cola de mensajes
        bus_mensajes.limpiar_cola()
        
        print("✅ Sistema cerrado correctamente")

if __name__ == "__main__":
    main()