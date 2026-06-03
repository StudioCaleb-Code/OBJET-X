import cv2
from ultralytics import YOLO
from productos_db import obtener_info_producto

# Cargar el modelo entrenado (usa 'yolov8n.pt' si aún no has entrenado el tuyo)
model = YOLO("runs/detect/train/weights/best.pt")

def procesar_imagen(ruta_imagen):
    img = cv2.imread(ruta_imagen)
    resultados = model(img)

    for r in list(resultados):
        for box in r.boxes:
            # Obtener coordenadas de la caja
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Obtener nombre de la clase detectada
            id_clase = int(box.cls[0])
            nombre_clase = model.names[id_clase]
            
            # Buscar info en nuestra "Base de datos"
            info = obtener_info_producto(nombre_clase)
            
            # Dibujar rectángulo
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Crear texto con Nombre, Categoría y Precio
            texto = f"{info['nombre']} ({info['categoria']}): ${info['precio']:.2f}"
            cv2.putText(img, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Guardar y mostrar resultado
    cv2.imwrite("resultado.jpg", img)
    cv2.imshow("OBJET-X - Deteccion de Imagen", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Prueba con una imagen local
    procesar_imagen("tu_foto_de_prueba.jpg")