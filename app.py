import os
import cv2
import pandas as pd
from flask import Flask, render_template, Response
from ultralytics import YOLO

# =====================================================================
# 0. CONFIGURACIÓN ROBUSTA DE RUTAS PARA EVITAR TEMPLATE_NOT_FOUND
# =====================================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

# =====================================================================
# 1. CARGAR EL MODELO YOLOv8
# =====================================================================
model = YOLO("best.pt")

# =====================================================================
# 2. CARGAR BASE DE DATOS EN MEMORIA (Optimiza el rendimiento)
# =====================================================================
def cargar_inventario():
    csv_path = os.path.join(BASE_DIR, "productos.csv")
    try:
        print("📦 Cargando inventario desde productos.csv...")
        return pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error crítico: No se encontró 'productos.csv'. Detalles: {e}")
        return pd.DataFrame(columns=['id_modelo', 'nombre', 'categoria', 'precio'])

# Variable global para mantener los productos cargados
df_productos = cargar_inventario()

def obtener_info_desde_csv(nombre_clase):
    nombre_limpio = nombre_clase.strip()
    global df_productos
    
    try:
        # Buscamos directamente en el DataFrame cargado en memoria
        producto_encontrado = df_productos[df_productos['id_modelo'] == nombre_limpio]
        if not producto_encontrado.empty:
            fila = producto_encontrado.iloc[0]
            return {
                "nombre": fila['nombre'],
                "categoria": fila['categoria'],
                "precio": float(fila['precio'])
            }
    except Exception as e:
        print(f"⚠️ Error procesando datos de clase '{nombre_limpio}': {e}")
        
    return {"nombre": f"Desconocido ({nombre_limpio})", "categoria": "General", "precio": 0.00}

# =====================================================================
# 3. GENERADOR DE STREAMING DE VIDEO EN VIVO (CORREGIDO Y SEGURO)
# =====================================================================
# =====================================================================
# 3. GENERADOR DE STREAMING DE VIDEO EN VIVO (CORREGIDO PARA WINDOWS)
# =====================================================================
def generar_frames():
    # cv2.CAP_DSHOW obliga a Windows a usar DirectShow en lugar de MSMF, evitando el bug de lectura
    camara = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # Configuramos parámetros de video compatibles con cualquier webcam integrada/USB
    camara.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camara.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camara.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # Fuerza formato comprimido rápido
    
    if not camara.isOpened():
        print("❌ Error: No se pudo acceder a la cámara web usando DirectShow.")
        return

    try:
        while True:
            suceso, frame = camara.read()
            if not suceso:
                # En lugar de romper el bucle al primer micro-lag, saltamos al siguiente frame
                continue
            
            # Procesamiento de IA con YOLOv8
            resultados = model(frame, stream=True)
            
            for r in resultados:
                for box in r.boxes:
                    confianza = float(box.conf[0])
                    if confianza > 0.4:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        id_clase = int(box.cls[0])
                        nombre_clase = model.names[id_clase]
                        
                        info = obtener_info_desde_csv(nombre_clase)
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        texto = f"{info['nombre']}: S/. {info['precio']:.2f}"
                        cv2.putText(frame, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Codificación JPG para el navegador
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    finally:
        print("🔌 Liberando el recurso de la cámara de manera segura...")
        camara.release()
# =====================================================================
# 4. RUTAS DEL SERVIDOR WEB FLASK
# =====================================================================
@app.route('/')
def index():
    # Recargamos dinámicamente el CSV en memoria cada vez que se entra al Home,
    # permitiendo cambiar los precios desde Excel sin apagar el servidor de IA.
    global df_productos
    df_productos = cargar_inventario()
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Ruta que alimenta la etiqueta img de tu HTML para mostrar la cámara con YOLOv8"""
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/nosotros')
def nosotros():
    return render_template('pages/nosotros.html')

@app.route('/documentacion')
def documentacion():
    return render_template('pages/documentacion.html')

@app.route('/repositorio')
def repositorio():
    return render_template('pages/repositorio.html')

# =====================================================================
# 5. ENCENDIDO DEL SERVIDOR
# =====================================================================
if __name__ == '__main__':
    # use_reloader=False es obligatorio con OpenCV para evitar el doble hilo colisionado
    app.run(debug=True, use_reloader=False, port=5000)