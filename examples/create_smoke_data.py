"""Generate explicitly synthetic operation tests; no business-accuracy claim."""
import csv
from pathlib import Path

texts = {
    "urgente": ["El sistema de pedidos está caído.", "Nadie puede acceder a la plataforma.",
                "La caja está bloqueada y no podemos cobrar.", "No podemos procesar ninguna venta.",
                "El servicio dejó de funcionar para todos.", "El equipo no puede trabajar por un fallo.",
                "Los pedidos están detenidos por una avería.", "Se bloqueó el acceso de todos los operadores.",
                "No hay alternativa para continuar la operación.", "Una caída impide atender a los clientes."],
    "normal": ["Actualiza el documento cuando puedas.", "Quiero cambiar el color del panel.",
               "Podemos revisar el informe la próxima semana.", "Añade un filtro cuando tengas tiempo.",
               "Sin prisa, corrige el título del documento.", "Necesito una copia del manual para mañana.",
               "La operación funciona; propongo mejorar el diseño.", "No hay bloqueo, es una mejora futura.",
               "Podemos esperar para modificar la plantilla.", "Solicito una reunión para organizar mejoras."],
    "revision": ["No sé si la plataforma funciona.", "Quizás exista un problema; falta confirmarlo.",
                 "Dicen que es urgente, pero puede esperar.", "Necesito ayuda y no sé explicar qué sucede.",
                 "Faltan datos sobre el impacto del incidente.", "Un usuario dice que funciona y otro que no.",
                 "Tal vez esté bloqueado; no tengo información.", "No conozco el estado actual del servicio.",
                 "Hay versiones contradictorias sobre el fallo.", "No se ha confirmado si existe un bloqueo."]}

path = Path(__file__).with_name("synthetic.csv")
with path.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=["text", "answer", "group", "language", "origin"])
    writer.writeheader()
    for label, values in texts.items():
        for index, text in enumerate(values):
            writer.writerow(dict(text=text, answer=label, group=f"{label}-{index}", language="es", origin="synthetic"))
print(path)
