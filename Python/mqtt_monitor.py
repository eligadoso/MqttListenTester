import websocket
import json
import threading
import time
from datetime import datetime
import base64
import os

# Importar configuración desde archivo separado
from config import (
    WS_URL, USERNAME, PASSWORD, LOG_FILE, 
    RECONNECT_DELAY, MAX_RECONNECT_ATTEMPTS, SPECIFIC_NODES
)

class SpecificNodesMonitor:
    def __init__(self):
        self.message_count = 0
        self.nodes_seen = set()
        self.ws = None
        self.should_reconnect = True
        self.reconnect_attempts = 0
        self.is_connected = False
        self.subscribed_topics = []
        
        # Crear archivo de log si no existe
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write(f"=== SmartBee Monitor - Nodos Específicos - Iniciado: {self.get_timestamp()} ===")
                f.write("Nodos monitoreados:\n")
                for node in SPECIFIC_NODES:
                    f.write(f"  - {node}\n")
                f.write("\nFormato: [TIMESTAMP] TOPIC | NODO | DATOS\n")
                f.write("=" * 100 + "\n")
        
    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def log_to_file(self, topic, message, payload_data=None):
        """Guardar mensaje en archivo de texto"""
        timestamp = self.get_timestamp()
        
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                if payload_data:
                    # Si tenemos datos estructurados
                    node_id = payload_data.get('nodo_id', 'DESCONOCIDO')
                    temp = payload_data.get('temperatura', 'N/A')
                    hum = payload_data.get('humedad', 'N/A')
                    peso = payload_data.get('peso', 'N/A')
                    
                    log_line = f"[{timestamp}] {topic} | {node_id} | TEMP:{temp}°C HUM:{hum}% PESO:{peso}kg\n"
                else:
                    # Mensaje raw
                    log_line = f"[{timestamp}] {topic} | RAW | {message}\n"
                    
                f.write(log_line)
                f.flush()  # Asegurar que se escriba inmediatamente
                
        except Exception as e:
            print(f"❌ Error escribiendo al archivo: {e}")
        
    def on_message(self, ws, message):
        self.message_count += 1
        timestamp = self.get_timestamp()
        
        print(f"📨 [{timestamp}] Mensaje #{self.message_count}")
        
        try:
            data = json.loads(message)
            
            # Verificar si es un mensaje MQTT con topic y payload
            if isinstance(data, dict) and 'topic' in data and 'payload' in data:
                topic = data['topic']
                payload_str = data['payload']
                
                # Verificar si el tópico corresponde a uno de nuestros nodos específicos
                node_from_topic = None
                for node in SPECIFIC_NODES:
                    expected_topic = f"SmartBee/nodes/{node}/data"
                    if topic == expected_topic:
                        node_from_topic = node
                        break
                
                if node_from_topic:
                    print(f"   ✅ Nodo específico detectado: {node_from_topic}")
                else:
                    print(f"   ⚠️  Nodo no específico: {topic}")
                
                try:
                    # Intentar parsear el payload como JSON
                    payload_data = json.loads(payload_str)
                    
                    # Extraer información del nodo
                    node_id = payload_data.get('nodo_id', 'DESCONOCIDO')
                    if node_id != 'DESCONOCIDO':
                        self.nodes_seen.add(node_id)
                    
                    print(f"   📍 Tópico: {topic}")
                    print(f"   🏷️  Nodo ID: {node_id}")
                    
                    # Verificar consistencia
                    if node_from_topic and node_id != node_from_topic:
                        print(f"   ⚠️  INCONSISTENCIA: Tópico indica {node_from_topic} pero payload indica {node_id}")
                    
                    # Mostrar datos del sensor
                    if 'temperatura' in payload_data:
                        print(f"   🌡️  Temperatura: {payload_data['temperatura']}°C")
                    if 'humedad' in payload_data:
                        print(f"   💧 Humedad: {payload_data['humedad']}%")
                    if 'peso' in payload_data:
                        print(f"   ⚖️  Peso: {payload_data['peso']} kg")
                    
                    print(f"   📄 Payload: {json.dumps(payload_data, ensure_ascii=False)}")
                    
                    # Guardar en archivo solo si es de nuestros nodos específicos
                    if node_from_topic:
                        self.log_to_file(topic, payload_str, payload_data)
                        print(f"   💾 ✅ Guardado en {LOG_FILE}")
                    else:
                        print(f"   💾 ⏭️  No guardado (nodo no específico)")
                    
                except json.JSONDecodeError:
                    # Payload no es JSON válido
                    print(f"   📍 Tópico: {topic}")
                    print(f"   📄 Payload (texto): {payload_str}")
                    
                    # Guardar solo si es de nuestros nodos específicos
                    if node_from_topic:
                        self.log_to_file(topic, payload_str)
                        print(f"   💾 ✅ Guardado en {LOG_FILE}")
                    
            else:
                # Mensaje de control o estado
                print(f"   🔧 Mensaje de control: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
        except json.JSONDecodeError:
            print(f"   📄 Mensaje raw: {message}")
            
        print("-" * 80)
        
        # Mostrar estadísticas cada 3 mensajes
        if self.message_count % 3 == 0:
            self.show_stats()
    
    def on_error(self, ws, error):
        print(f"❌ [{self.get_timestamp()}] Error WebSocket: {error}")
        self.is_connected = False
        
    def on_close(self, ws, close_status_code, close_msg):
        print(f"🔌 [{self.get_timestamp()}] Conexión cerrada. Código: {close_status_code}")
        self.is_connected = False
        
        if self.should_reconnect and self.reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
            self.reconnect_attempts += 1
            print(f"🔄 Intento de reconexión #{self.reconnect_attempts} en {RECONNECT_DELAY} segundos...")
            time.sleep(RECONNECT_DELAY)
            self.connect()
        elif self.reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
            print(f"❌ Máximo número de intentos de reconexión alcanzado ({MAX_RECONNECT_ATTEMPTS})")
            self.should_reconnect = False
        
    def on_open(self, ws):
        print(f"✅ [{self.get_timestamp()}] Conexión WebSocket establecida")
        self.is_connected = True
        self.reconnect_attempts = 0  # Resetear contador de reconexiones
        
        # Intentar autenticación
        auth_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "action": "connect"
        }
        
        ws.send(json.dumps(auth_data))
        print("🔐 Datos de autenticación enviados")
        
        # Suscribirse a cada nodo específico
        print(f"📡 Suscribiéndose a {len(SPECIFIC_NODES)} nodos específicos...")
        
        for i, node_id in enumerate(SPECIFIC_NODES, 1):
            topic = f"SmartBee/nodes/{node_id}/data"
            subscribe_data = {
                "action": "subscribe",
                "topic": topic
            }
            
            ws.send(json.dumps(subscribe_data))
            self.subscribed_topics.append(topic)
            print(f"   {i}. ✅ {topic}")
            
            # Pequeña pausa entre suscripciones para evitar saturar
            time.sleep(0.1)
        
        print(f"📡 ✅ Suscripción completada a {len(self.subscribed_topics)} tópicos")
        print("👂 Escuchando mensajes de nodos específicos...")
        print(f"💾 Guardando mensajes en: {LOG_FILE}")
        print("-" * 80)
        
    def show_stats(self):
        print(f"📊 ESTADÍSTICAS:")
        print(f"   📨 Mensajes recibidos: {self.message_count}")
        print(f"   🎯 Nodos específicos monitoreados: {len(SPECIFIC_NODES)}")
        print(f"   📡 Tópicos suscritos: {len(self.subscribed_topics)}")
        print(f"   🏷️  Nodos activos detectados: {len(self.nodes_seen)}")
        print(f"   🔄 Intentos de reconexión: {self.reconnect_attempts}")
        print(f"   🔗 Estado: {'Conectado' if self.is_connected else 'Desconectado'}")
        
        if self.nodes_seen:
            active_specific = [node for node in self.nodes_seen if node in SPECIFIC_NODES]
            print(f"   ✅ Nodos específicos activos: {len(active_specific)}")
            if active_specific:
                print(f"      {', '.join(sorted(active_specific))}")
        print("-" * 80)
        
    def connect(self):
        """Establecer conexión WebSocket"""
        try:
            # Crear headers de autenticación
            auth_string = f"{USERNAME}:{PASSWORD}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}"
            }
            
            self.ws = websocket.WebSocketApp(
                WS_URL,
                header=headers,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Ejecutar en un hilo separado para permitir reconexión
            self.ws.run_forever()
            
        except Exception as e:
            print(f"❌ Error en conexión: {e}")
            if self.should_reconnect:
                time.sleep(RECONNECT_DELAY)
                self.connect()
        
    def start_monitoring(self):
        print("🚀 Iniciando monitor SmartBee - Nodos Específicos")
        print(f"⏰ Hora de inicio: {self.get_timestamp()}")
        print(f"🔗 URL: {WS_URL}")
        print(f"👤 Usuario: {USERNAME}")
        print(f"💾 Archivo de log: {LOG_FILE}")
        print(f"🎯 Nodos específicos a monitorear: {len(SPECIFIC_NODES)}")
        
        print("\n📋 Lista de nodos:")
        for i, node in enumerate(SPECIFIC_NODES, 1):
            print(f"   {i}. {node}")
        
        print(f"\n🔄 Reconexión automática: Habilitada (máx. {MAX_RECONNECT_ATTEMPTS} intentos)")
        print("=" * 80)
        
        try:
            self.connect()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo monitor...")
            self.should_reconnect = False
            if self.ws:
                self.ws.close()
            self.show_stats()
            print(f"💾 Mensajes guardados en: {LOG_FILE}")
            print("✅ Monitor detenido")

if __name__ == "__main__":
    monitor = SpecificNodesMonitor()
    monitor.start_monitoring()