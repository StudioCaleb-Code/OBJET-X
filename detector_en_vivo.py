import cv2
from ultralytics import YOLO
from productos_db import obtener_info_producto

# Cargar modelo
model = YOLO("runs/detect/train/weights/best.pt")

# Iniciar captura de video (0 suele ser la webcam integrada)
cap = cv2.VideoCapture(0)

print("📷 Presiona 'q' para salir del detector en vivo.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Hacer la predicción frame por frame
    resultados = model(frame, stream=True)

    for r in resultados:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            id_clase = int(box.cls[0])
            nombre_clase = model.names[id_clase]
            
            # Confianza de la predicción
            confianza = box.conf[0]
            
            if confianza > 0.5: # Solo mostrar si está más del 50% seguro
                info = obtener_info_producto(nombre_clase)
                
                # Dibujar en pantalla
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                texto = f"{info['nombre']} - ${info['precio']:.2f}"
                cv2.putText(frame, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    cv2.imshow("OBJET-X - Tiempo Real", frame)

    # Romper bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()