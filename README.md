# Julia Fine-tuning para Portable Agent Workspace

**[Guía para usuarios](https://mauricioperera.github.io/julia-finetune-workspace/)** ·
**[Prompt de instalación asistida](https://mauricioperera.github.io/julia-finetune-workspace/prompt.md)** ·
**[Versión 0.1.0](https://github.com/MauricioPerera/julia-finetune-workspace/releases/tag/v0.1.0)**

Herramienta independiente; no afiliada a Supersonic Labs. El código de esta
herramienta usa licencia MIT. Julia-1 se descarga de su repositorio oficial y
sus artefactos mantienen su licencia Apache 2.0.

Primera versión local. Entrenador de decisiones `choice` por CPU,
operable mediante un agente con archivos y terminal. No modifica la plantilla
original ni servicios existentes. Véase [contrato](CONTRACT.md) y
[prompt para agentes](docs/prompt.md).

## Formato de entrada

`task.json`: pregunta y mapa de identificadores a descripciones, como en
`examples/task.json`. CSV o JSONL: `text`, `answer`, opcionalmente `group`,
`language`, `origin`. Cada línea contiene un ejemplo. `answer` debe ser un
identificador de la configuración. No se requiere conocimiento de tokenización.

Los grupos mantienen juntos ejemplos relacionados. Se comprueban duplicados
mediante NFC, espacios y casefold; detectar paráfrasis semánticas requiere revisión.
La separación busca aproximadamente 60/20/20 por grupos con todas las categorías
en cada partición. Pocos datos pueden impedir una separación válida.

## Instalación aislada

```sh
python scripts/bootstrap.py --destination /ruta/nueva/julia-runtime
```

Python >=3.11. Modelo fijado a la revisión
`a85b127321d580d65176c89ced8273f305745d85` de SupersonicLabs/Julia-1.
Torch CPU 2.12.0 y dependencias principales y transitivas fijadas mediante
constraints-cpu.txt. environment.txt registra las versiones instaladas. No se
incluyen hashes de wheels para todas las plataformas. Probado en Windows con
Python 3.14 y Ubuntu con Python 3.12; otros entornos requieren su primer uso.

## Entrenamiento

Usa el Python del entorno aislado:

```sh
python -m julia_finetune.cli validate --config task.json --data ejemplos.csv
python -m julia_finetune.cli train --model /ruta/julia-runtime/Julia-1 --config task.json --data ejemplos.csv --output /ruta/resultados/nuevo
```

Por defecto se congela el encoder y se entrenan los componentes de decisión
activos. `--mode full` permite ajustar también el encoder. La cabeza de acciones
no se usa ni entrena para choice. Esto no certifica otras tareas ni idiomas.
El encoding es estricto: se rechazan textos que excedan el presupuesto.

El estado se guarda después de cada lote. Para continuar, repite la orden con
`--resume` y las mismas opciones. `--max-steps` permite interrumpir limpiamente
una prueba; no cambia la identidad del entrenamiento. RUNNING.lock mantiene un
bloqueo del sistema operativo, liberado automáticamente si el proceso muere.
El archivo permanece por diseño: no lo borres durante una ejecución.

selected/ contiene el checkpoint elegido por macro-F1 de validación. report.json
compara original y ajustado en la misma prueba e incluye métricas por categoría
e idioma, hashes, pérdida y comprobación de recarga. Los datos y resultados son
locales y pueden contener textos privados; no se publican automáticamente.

Puedes recalcular las métricas guardadas y probar un texto:

```sh
python -m julia_finetune.cli verify --run /ruta/resultados/nuevo --original /ruta/julia-runtime/Julia-1
python -m julia_finetune.cli predict --model /ruta/resultados/nuevo/selected --config task.json --text "El sistema está bloqueado"
```

`scripts/install_workspace.py` crea una instancia nueva de la plantilla y añade
la capacidad opcional. Sigue el prompt para revisar y verificar la distribución
original antes de ejecutarlo. No modifica el distribuidor ni workspaces existentes.

## Estado de verificación

Siete pruebas de datos y bloqueo pasan en Windows y Linux. La instalación aislada,
el entrenamiento con pesos reales y la recarga funcionan en ambos sistemas.
La integración opcional en una instancia nueva se verificó en Linux. La ejecución
continua y la recuperación tras muerte abrupta producen exactamente los mismos
tensores e historial; se rechaza reanudar con datos cambiados. Los informes de
la prueba sintética pequeña dan 3/6 antes y después: no demuestran mejora de calidad.
La verificación principal usa mode=head; mode=full es una opción avanzada todavía
sin una prueba completa de integración y no se recomienda como ruta inicial.
