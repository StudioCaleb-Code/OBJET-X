import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from ultralytics import YOLO

# =====================================================================
# 1. CONFIGURACIÓN VISUAL Y ESTILOS DE LA PÁGINA
# =====================================================================
st.set_page_config(
    page_title="OBJET-X Dashboard", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Avanzados para controlar el diseño visual
st.markdown("""
    <style>
    /* Estilo del título principal */
    .titulo-principal {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #FF4B4B;
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    /* Subtítulo descriptivo */
    .subtitulo {
        text-align: center;
        color: #A0A0A0;
        font-size: 18px;
        margin-bottom: 30px;
    }
    /* Estilo premium de tarjetas de precios */
    .tarjeta-precio {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00E676;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado visual del Dashboard
st.markdown('<div class="titulo-principal">🔮 OBJET-X CORE SYSTEMS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Terminal Inteligente de Reconocimiento de Productos y Precios en Tiempo Real</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================================================
# 2. FUNCIONES NATIVAS DE IA Y BASE DE DATOS
# =====================================================================
@st.cache_resource
def cargar_modelo():
    """Carga el cerebro de YOLOv8 de manera eficiente."""
    return YOLO("best.pt")

model = cargar_modelo()

def obtener_info_desde_csv(nombre_clase):
    """Busca los datos comerciales del producto dentro del archivo CSV."""
    nombre_limpio = nombre_clase.strip()
    try:
        df = pd.read_csv("productos.csv")
        # Filtrar fila donde coincida el id_modelo detectado por la IA
        producto_encontrado = df[df['id_modelo'] == nombre_limpio]
        
        if not producto_encontrado.empty:
            fila = producto_encontrado.iloc[0]
            return {
                "nombre": fila['nombre'],
                "categoria": fila['categoria'],
                "precio": float(fila['precio'])
            }
    except Exception as e:
        print(f"❌ Error crítico leyendo productos.csv: {e}")
        
    # Retorno seguro si el producto no está registrado en el CSV
    return {
        "nombre": f"Desconocido ({nombre_limpio})",
        "categoria": "No Registrada",
        "precio": 0.00
    }

def procesar_deteccion(imagen_pil):
    """Procesa los píxeles, dibuja los recuadros y extrae los precios."""
    img = np.array(imagen_pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    resultados = model(img)
    lista_detecciones = []

    for r in resultados:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            id_clase = int(box.cls[0])
            nombre_clase = model.names[id_clase]
            confianza = float(box.conf[0])
            
            # Filtro de seguridad (Evita falsos positivos menores al 40%)
            if confianza > 0.4:
                info = obtener_info_desde_csv(nombre_clase)
                lista_detecciones.append(info)
                
                # Dibujar recuadro de diseño verde brillante
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 230, 118), 3)
                
                # Añadir etiqueta de texto flotante en la imagen
                texto_pantalla = f"{info['nombre']}: ${info['precio']:.2f}"
                cv2.putText(img, texto_pantalla, (x1, y1 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 118), 2)
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb, lista_detecciones

# =====================================================================
# 3. INTERFAZ GRÁFICA DE USUARIO (GUI)
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2543/2543369.png", width=100)
    st.header("⚙️ Panel de Control")
    opcion = st.selectbox(
        "Elige la modalidad del escáner:",
        ["📸 Subir Imagen Manual", "📷 Escáner en Tiempo Real"]
    )
    st.write("---")
    if st.checkbox("📊 Ver Inventario y Precios (CSV)"):
        st.dataframe(pd.read_csv("productos.csv"), hide_index=True)

# Distribución de la pantalla en dos bloques asimétricos
col_izquierda, col_derecha = st.columns([1.2, 1.0], gap="large")

# --- MODALIDAD A: SUBIR IMAGEN MANUAL ---
if opcion == "📸 Subir Imagen Manual":
    with col_izquierda:
        st.subheader("🖼️ Entrada de Archivo")
        archivo = st.file_uploader("Arrastra o selecciona la fotografía de tus productos:", type=["jpg", "png", "jpeg"])
        
        if archivo:
            imagen_original = Image.open(archivo)
            st.image(imagen_original, caption="Imagen de origen cargada", width='stretch')
            ejecutar = st.button("🔍 INICIAR ESCANEO", type="primary")

    with col_derecha:
        st.subheader("📊 Resultados del Análisis")
        if archivo and ejecutar:
            with st.spinner("Analizando estructuras y consultando precios..."):
                img_dibujada, productos_encontrados = procesar_deteccion(imagen_original)
            
            st.image(img_dibujada, caption="Resultado del escaneo inteligente", width='stretch')
            
            if productos_encontrados:
                total_caja = 0
                st.markdown("### 🛒 Lista de Productos:")
                for prod in productos_encontrados:
                    total_caja += prod['precio']
                    st.markdown(f"""
                        <div class="tarjeta-precio">
                            <span style='font-size:12px; color:#A0A0A0; text-transform:uppercase;'>{prod['categoria']}</span>
                            <h4 style='margin:2px 0; color:#FFF;'>{prod['nombre']}</h4>
                            <h3 style='margin:0; color:#00E676;'>${prod['precio']:.2f}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.metric(label="💰 TOTAL DEL CARRITO", value=f"${total_caja:.2f}")
            else:
                st.error("No se encontraron detecciones válidas en esta imagen.")

# --- MODALIDAD B: ESCÁNER POR CÁMARA (TIEMPO REAL) ---
elif opcion == "📷 Escáner en Tiempo Real":
    with col_izquierda:
        st.subheader("🎥 Captura en Vivo")
        st.write("Coloca los productos directamente frente a la lente de tu cámara.")
        foto_camara = st.camera_input("Capturar cuadro del escáner:")

    with col_derecha:
        st.subheader("📊 Resultados del Análisis")
        if foto_camara:
            imagen_camara = Image.open(foto_camara)
            with st.spinner("Decodificando información visual..."):
                img_dibujada, productos_encontrados = procesar_deteccion(imagen_camara)
            
            st.image(img_dibujada, caption="Análisis instantáneo completado", width='stretch')
            
            if productos_encontrados:
                total_caja = 0
                st.markdown("### 🛒 Detalle de Cuenta:")
                for prod in productos_encontrados:
                    total_caja += prod['precio']
                    st.markdown(f"""
                        <div class="tarjeta-precio">
                            <span style='font-size:12px; color:#A0A0A0; text-transform:uppercase;'>{prod['categoria']}</span>
                            <h4 style='margin:2px 0; color:#FFF;'>{prod['nombre']}</h4>
                            <h3 style='margin:0; color:#00E676;'>${prod['precio']:.2f}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.metric(label="💰 TOTAL DEL CARRITO", value=f"${total_caja:.2f}")
            else:
                st.warning("Cámara activa. Coloca un producto registrado para calcular los costos automáticamente.")