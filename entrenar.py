from ultralytics import YOLO

def entrenar_modelo():
    # Cargamos un modelo base preentrenado (YOLOv8 nano, que es ligero y rápido)
    model = YOLO("yolov8n.pt") 

    print("🚀 Iniciando el entrenamiento de OBJET-X...")
    # Entrenar el modelo
    model.train(
        data="data.yaml",   # Archivo de configuración
        epochs=50,          # Cantidad de vueltas de entrenamiento (ajustable)
        imgsz=640,          # Tamaño de la imagen
        device="cpu"        # Cambia a "cuda" si tienes tarjeta gráfica Nvidia
    )
    print("✅ ¡Entrenamiento completado! El modelo se guardó en 'runs/detect/train/weights/best.pt'")

if __name__ == "__main__":
    entrenar_modelo()