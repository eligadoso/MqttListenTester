# Configuración para SmartBee MQTT Monitor

# Configuración de conexión WebSocket
WS_URL = "wss://www.smartbee.cl/apps/mqtt.read.rcr"
USERNAME = "NODO-B51D175B-9B00-4CBD-B4C1-2597C0258F26"
PASSWORD = "dohph3roo0ahmeiFee9v"

# Configuración de archivos y logs
LOG_FILE = "smartbee_specific_nodes.txt"

# Configuración de reconexión
RECONNECT_DELAY = 5  # segundos
MAX_RECONNECT_ATTEMPTS = 10

# Lista de nodos específicos de la imagen
SPECIFIC_NODES = [
    "NODO-8CF65C52-FACE-42A3-B6D8-87DD82AEDA56",
    "NODO-DF38B47D-4D2B-4EBB-95D7-E0B38335607D",
    "NODO-10B8AA62-6F39-4C50-AADD-2414A0BCFD62",
    "NODO-C8C80453-1D45-4CE8-9B5A-EB55E5349F16",
    "NODO-3E3ABA4B-AF98-46F9-A4EA-EF136E073172",
    "NODO-C3BB9768-A6C5-40A2-B0FF-A1F6C78355C4"
]