# Qué se verificó en la versión 0.1.0

Herramienta independiente para adaptar decisiones de selección (`choice`) de
Julia-1. Modelo fijado a la revisión
`a85b127321d580d65176c89ced8273f305745d85` de
[SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1).

## Pruebas realizadas el 29 de septiembre de 2026

- Instalación aislada y dependencias sin conflictos: Windows/Python 3.14 y
  Ubuntu/Python 3.12, por CPU.
- Entrenamiento con pesos reales, gradientes finitos y no nulos y cambios de pesos.
- Modelo original conservado, checkpoint ajustado guardado y recargado mediante
  el runtime de Julia, con predicciones coincidentes.
- Métricas recalculadas por el comando `verify`, usando nuevas inferencias.
- Reanudación después de matar el proceso: historial y todos los tensores
  exactamente iguales a los de una ejecución continua.
- Reanudación con datos modificados rechazada.
- Siete pruebas de importación, validación, separación por grupos y bloqueo
  de ejecuciones simultáneas, en ambas plataformas.
- Capacidad opcional instalada en instancias nuevas del Portable Agent Workspace,
  con validadores de estructura, primer uso y contrato Julia correctos.
- Instalación Linux desde el paquete de distribución y primer uso completo.

## Resultado de la prueba sintética

30 ejemplos ficticios en español: 18 para entrenar, 6 para validar y 6 para probar.
Una época, nueve lotes. Se entrenaron 3.699.073 parámetros de los componentes
de decisión, manteniendo congelado el encoder.

| Modelo | Aciertos en prueba |
|---|---|
| Original | 3 de 6 |
| Ajustado | 3 de 6 |

La prueba confirmó el funcionamiento de la herramienta. **No demostró una mejora
de precisión.** Tampoco mide rendimiento con datos reales de un nicho ni
conservación de capacidades multilingües.

## Límites de la primera versión

- La ruta verificada es entrenamiento por CPU en modo `head`. El modo `full`
  es una opción avanzada sin prueba completa de integración.
- Las paráfrasis y traducciones relacionadas necesitan un identificador de grupo
  y revisión para evitar que crucen entre entrenamiento y prueba.
- Las versiones de dependencias están fijadas; no hay un catálogo de hashes
  de wheels para todas las plataformas.
- Los hashes detectan cambios respecto del registro; no son firmas independientes.
- El comando `predict` usa las probabilidades redondeadas del API legacy de Julia.
  No deben interpretarse como certeza garantizada.
- La integración del workspace referencia rutas locales. Moverlo a otro equipo
  requiere reinstalar el entorno y actualizar esas referencias.
- Una IA asistente necesita acceso real a archivos y terminal. La página web
  no ejecuta el entrenamiento.

[Volver a la guía](index.html) · [Leer el código](https://github.com/MauricioPerera/julia-finetune-workspace)
