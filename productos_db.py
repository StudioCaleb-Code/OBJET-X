# Base de datos simulada
PRODUCTOS = {
    "Agua": {
        "nombre": "Agua",
        "categoria": "Bebidas",
        "precio": 1.50
    },
    "papas_fritas": {
        "nombre": "Papas Fritas Originales",
        "categoria": "Snacks",
        "precio": 2.10
    },
    "galletas_chocolate": {
        "nombre": "Galletas de Chocolate",
        "categoria": "Repostería / Dulces",
        "precio": 1.80
    }
}

def obtener_info_producto(nombre_clase):
    """Devuelve la información si existe, o valores por defecto."""
    return PRODUCTOS.get(nombre_clase, {"nombre": nombre_clase, "categoria": "Desconocida", "precio": 0.0})