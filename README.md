# SmartBee MQTT Monitor

Monitor en tiempo real para nodos específicos de SmartBee que se conecta vía WebSocket MQTT y registra los datos de sensores en archivos de log.

## 📋 Descripción

Este proyecto permite monitorear nodos específicos de SmartBee, capturando datos de sensores como temperatura, humedad y peso. Los datos se guardan automáticamente en archivos de texto para su posterior análisis.

## 🚀 Características

- ✅ Conexión WebSocket MQTT a SmartBee
- 🎯 Monitoreo de nodos específicos configurables
- 📊 Captura de datos de sensores (temperatura, humedad, peso)
- 💾 Guardado automático en archivos de log
- 🔄 Reconexión automática en caso de pérdida de conexión
- 📈 Estadísticas en tiempo real
- ⚙️ Configuración separada para fácil mantenimiento

## 📦 Instalación

### Requisitos previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Dependencias

Instala las dependencias necesarias:

```bash
pip install websocket-client
```

### Configuración

1. **Copia el archivo de configuración de ejemplo:**
   ```bash
   cp config.example.py config.py
   ```

2. **Edita el archivo `config.py` con tus credenciales:**
   ```python
   # Configuración de conexión WebSocket
   WS_URL = "wss://www.smartbee.cl/apps/mqtt.read.rcr"
   USERNAME = "TU_USUARIO_AQUI"
   PASSWORD = "TU_PASSWORD_AQUI"
   
   # Lista de nodos específicos a monitorear
   SPECIFIC_NODES = [
       "NODO-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
       # Agrega más nodos aquí
   ]
   ```

## 🎯 Uso

### Ejecución básica

```bash
python mqtt_monitor.py
```

### Ejecución en segundo plano (Linux/Mac)

```bash
nohup python mqtt_monitor.py > monitor.log 2>&1 &
```

### Ejecución en segundo plano (Windows)

```cmd
start /B python mqtt_monitor.py
```

## 📁 Estructura del proyecto
