"""Generate the three static technical guides using only the standard library."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://mauricioperera.github.io/julia-finetune-workspace/'
REPO = 'https://github.com/MauricioPerera/julia-finetune-workspace'


def localized(values, index):
    return html.escape(values[index])


# Each entry contains reviewed Spanish, English and Portuguese text.
SECTIONS = [
    ('architecture', ('Arquitectura y alcance', 'Architecture and scope', 'Arquitetura e escopo'), [
        ('Julia-1 es un modelo de decisiones de 144,3 M de parámetros. Esta herramienta adapta únicamente tareas choice: estado del texto, pregunta y opciones descritas → categoría seleccionada. No añade generación de texto libre ni entrena la cabeza de acciones.',
         'Julia-1 is a decision model with 144.3 M parameters. This tool adapts choice tasks only: text state, question and described options → selected category. It does not add free-form text generation or train the action head.',
         'Julia-1 é um modelo de decisões com 144,3 M de parâmetros. Esta ferramenta adapta apenas tarefas choice: estado do texto, pergunta e opções descritas → categoria selecionada. Não adiciona geração de texto livre nem treina a cabeça de ações.'),
        ('El entrenador usa PyTorch en CPU, float32, AdamW y algoritmos deterministas. En mode=head congela el encoder y ajusta los componentes de decisión activos. El modo full también permite ajustar el encoder, pero carece de una prueba completa de integración.',
         'The trainer uses PyTorch on CPU, float32, AdamW and deterministic algorithms. In mode=head it freezes the encoder and trains the active decision components. Full mode also allows training the encoder, but lacks a complete integration test.',
         'O treinamento usa PyTorch em CPU, float32, AdamW e algoritmos determinísticos. No mode=head, congela o encoder e ajusta os componentes de decisão ativos. O modo full também permite ajustar o encoder, mas não tem um teste completo de integração.')]),
    ('setup', ('Instalación reproducible', 'Reproducible setup', 'Instalação reproduzível'), [
        ('Python ≥3.11. Entornos verificados: Windows/Python 3.14 y Ubuntu/Python 3.12, ambos por CPU. Internet es necesario para descargar el modelo y las dependencias. El ZIP de la versión no incluye los pesos. No hay un mínimo de RAM ni una duración universal medidos: dependen del dataset y de los textos.',
         'Python ≥3.11. Verified environments: Windows/Python 3.14 and Ubuntu/Python 3.12, both on CPU. Internet is required to download the model and dependencies. The release ZIP does not include weights. No measured universal RAM minimum or training duration is available: these depend on the dataset and texts.',
         'Python ≥3.11. Ambientes verificados: Windows/Python 3.14 e Ubuntu/Python 3.12, ambos em CPU. Internet é necessária para baixar o modelo e as dependências. O ZIP da versão não inclui os pesos. Não há um mínimo de RAM nem uma duração universal medidos: dependem do dataset e dos textos.'),
        ('Descarga la versión 0.1.0 y su checksum; verifica el SHA-256 y las entradas del ZIP antes de extraerlo en una carpeta nueva. Lee README.md y CONTRACT.md. Ejecuta el bootstrap desde la distribución con un destino nuevo; crea un venv sin paquetes globales. Consulta el prompt para el procedimiento completo de comprobación.',
         'Download release 0.1.0 and its checksum; verify SHA-256 and ZIP entries before extracting into a new directory. Read README.md and CONTRACT.md. Run bootstrap from the distribution with a new destination; it creates a venv without global packages. See the prompt for the complete verification procedure.',
         'Baixe a versão 0.1.0 e seu checksum; verifique o SHA-256 e as entradas do ZIP antes de extrair em uma nova pasta. Leia README.md e CONTRACT.md. Execute o bootstrap a partir da distribuição com um novo destino; ele cria um venv sem pacotes globais. Consulte o prompt para o procedimento completo de verificação.'),
        ('Modelo fijado a la revisión a85b127321d580d65176c89ced8273f305745d85. Torch CPU 2.12.0; versiones principales y transitivas fijadas en constraints-cpu.txt. environment.txt registra las versiones instaladas. Los hashes detectan cambios; no son firmas independientes del autor.',
         'Model pinned to revision a85b127321d580d65176c89ced8273f305745d85. Torch CPU 2.12.0; direct and transitive dependency versions pinned in constraints-cpu.txt. environment.txt records installed versions. Hashes detect changes; they are not independent author signatures.',
         'Modelo fixado na revisão a85b127321d580d65176c89ced8273f305745d85. Torch CPU 2.12.0; versões principais e transitivas fixadas em constraints-cpu.txt. environment.txt registra as versões instaladas. Os hashes detectam alterações; não são assinaturas independentes do autor.')]),
    ('data', ('Contrato de datos', 'Data contract', 'Contrato de dados'), [
        ('task.json admite exclusivamente question y categories. La pregunta no puede estar vacía. Define entre 2 y 20 categorías con identificadores y descripciones no vacíos. answer debe coincidir exactamente con un identificador; los identificadores se ordenan para construir los índices del modelo.',
         'task.json accepts only question and categories. The question cannot be empty. Define 2–20 categories with nonempty identifiers and descriptions. answer must exactly match an identifier; identifiers are sorted to build model indices.',
         'task.json aceita exclusivamente question e categories. A pergunta não pode estar vazia. Defina entre 2 e 20 categorias com identificadores e descrições não vazios. answer deve corresponder exatamente a um identificador; os identificadores são ordenados para construir os índices do modelo.'),
        ('CSV o JSONL en UTF-8, con BOM opcional. Cada campo debe ser texto. Se rechazan campos desconocidos, encabezados CSV duplicados, textos vacíos, categorías desconocidas, duplicados normalizados y etiquetas contradictorias. La normalización usa NFC, casefold y espacios.',
         'CSV or JSONL in UTF-8, with an optional BOM. Every field must be a string. Unknown fields, duplicate CSV headers, empty texts, unknown categories, normalized duplicates and conflicting labels are rejected. Normalization uses NFC, casefold and whitespace.',
         'CSV ou JSONL em UTF-8, com BOM opcional. Todos os campos devem ser texto. Campos desconhecidos, cabeçalhos CSV duplicados, textos vazios, categorias desconhecidas, duplicatas normalizadas e rótulos contraditórios são rejeitados. A normalização usa NFC, casefold e espaços.'),
        ('El ejemplo siguiente muestra el formato; tres filas no constituyen un dataset suficiente para entrenar y evaluar.',
         'The example below shows the format; three rows do not form a sufficient dataset for training and evaluation.',
         'O exemplo abaixo mostra o formato; três linhas não constituem um dataset suficiente para treinar e avaliar.')]),
    ('validation', ('Validación y separación', 'Validation and splitting', 'Validação e divisão'), [
        ('La separación busca aproximadamente 60/20/20 por grupos, con semilla 42 y todas las categorías en entrenamiento, validación y prueba. Exige al menos tres grupos independientes por categoría; eso es necesario, pero no garantiza una separación válida ni una evaluación fiable.',
         'Splitting targets approximately 60/20/20 by group, using seed 42 and requiring every category in training, validation and test. At least three independent groups per category are required; this is necessary but does not guarantee a valid split or reliable evaluation.',
         'A divisão busca aproximadamente 60/20/20 por grupos, com semente 42 e todas as categorias no treinamento, validação e teste. Exige pelo menos três grupos independentes por categoria; isso é necessário, mas não garante uma divisão válida nem uma avaliação confiável.'),
        ('Traducciones, paráfrasis y registros de la misma fuente deben compartir group para evitar fuga entre particiones. Si omites group, se deriva del texto normalizado. Los duplicados semánticos requieren revisión humana o del agente; no se detectan automáticamente.',
         'Translations, paraphrases and records from the same source must share group to prevent leakage across partitions. If group is omitted, it is derived from normalized text. Semantic duplicates need human or agent review; they are not detected automatically.',
         'Traduções, paráfrases e registros da mesma fonte devem compartilhar group para evitar vazamento entre partições. Se group for omitido, será derivado do texto normalizado. Duplicatas semânticas exigem revisão humana ou do agente; não são detectadas automaticamente.'),
        ('validate comprueba configuración, registros y separación sin cargar los pesos. La tokenización se comprueba al entrenar o predecir mediante encoding estricto: si se excede el presupuesto, se rechaza la entrada, sin truncamiento silencioso. Superar validate no garantiza superar la comprobación de longitud.',
         'validate checks configuration, records and splitting without loading weights. Tokenization is checked during training or prediction using strict encoding: inputs over budget are rejected without silent truncation. Passing validate does not guarantee passing the length check.',
         'validate verifica configuração, registros e divisão sem carregar os pesos. A tokenização é verificada ao treinar ou prever com encoding estrito: entradas que excedem o orçamento são rejeitadas, sem truncamento silencioso. Passar em validate não garante passar na verificação de comprimento.')]),
    ('cli', ('CLI: entrenar, verificar y predecir', 'CLI: train, verify and predict', 'CLI: treinar, verificar e prever'), [
        ('Los comandos siguientes se ejecutan desde la distribución con el Python del entorno aislado. Sustituye las rutas de ejemplo por las tuyas. La salida de entrenamiento debe ser nueva y estar separada del modelo original. También existe el ejecutable julia-finetune dentro del venv.',
         'Run the following commands from the distribution using the isolated environment’s Python. Replace example paths with your own. The training output must be new and separate from the original model. The julia-finetune executable is also available inside the venv.',
         'Execute os comandos abaixo a partir da distribuição usando o Python do ambiente isolado. Substitua os caminhos de exemplo pelos seus. A saída do treinamento deve ser nova e separada do modelo original. O executável julia-finetune também está disponível no venv.'),
        ('Los estados esperados son VALID, COMPLETED y VERIFIED. --max-steps 1 produce INTERRUPTED de forma intencional para probar la reanudación. Los errores de entrada o de archivos capturados por la CLI terminan con código 2. predict devuelve answer y probabilities; las probabilidades redondeadas del API legacy no son una garantía de certeza.',
         'Expected statuses are VALID, COMPLETED and VERIFIED. --max-steps 1 intentionally produces INTERRUPTED to test resuming. Input or file errors caught by the CLI exit with code 2. predict returns answer and probabilities; rounded probabilities from the legacy API do not guarantee certainty.',
         'Os estados esperados são VALID, COMPLETED e VERIFIED. --max-steps 1 produz INTERRUPTED intencionalmente para testar a retomada. Erros de entrada ou arquivos capturados pela CLI terminam com código 2. predict retorna answer e probabilities; probabilidades arredondadas da API legacy não garantem certeza.')]),
    ('resume', ('Reanudación y artefactos', 'Resuming and artifacts', 'Retomada e artefatos'), [
        ('Repite la orden de entrenamiento con --resume y las mismas opciones. La identidad incluye configuración, hash del dataset y del modelo, parámetros, hash del código, versiones de Torch y Transformers y hash de las particiones. Si cambia, la reanudación se rechaza. --max-steps no forma parte de esa identidad.',
         'Repeat the training command with --resume and the same options. Identity includes configuration, dataset and model hashes, settings, code hash, Torch and Transformers versions and split hash. If it changes, resuming is rejected. --max-steps is not part of that identity.',
         'Repita o comando de treinamento com --resume e as mesmas opções. A identidade inclui configuração, hashes do dataset e do modelo, parâmetros, hash do código, versões de Torch e Transformers e hash das partições. Se mudar, a retomada será rejeitada. --max-steps não faz parte dessa identidade.'),
        ('El estado del modelo, optimizador, RNG y progreso se guarda después de cada lote. RUNNING.lock usa un bloqueo del sistema operativo, que se libera si muere el proceso; el archivo permanece por diseño. No lo borres durante la ejecución. Un informe COMPLETED existente se devuelve al reanudar una ejecución ya finalizada.',
         'Model, optimizer, RNG and progress state are saved after each batch. RUNNING.lock uses an operating-system lock that is released if the process dies; the file remains by design. Do not delete it during execution. An existing COMPLETED report is returned when resuming an already finished run.',
         'O estado do modelo, otimizador, RNG e progresso é salvo após cada lote. RUNNING.lock usa um bloqueio do sistema operacional, liberado se o processo morrer; o arquivo permanece por design. Não o apague durante a execução. Um relatório COMPLETED existente é retornado ao retomar uma execução já concluída.')]),
    ('evaluation', ('Evaluación y aceptación', 'Evaluation and acceptance', 'Avaliação e aceitação'), [
        ('selected/ se elige por macro-F1 de validación. El informe compara el modelo original y el ajustado sobre la misma prueba reservada, con accuracy, macro-F1 y métricas por categoría e idioma. Usa casos reales separados para decidir si la mejora es suficiente para tu aplicación; no ajustes la prueba para obtener un resultado favorable.',
         'selected/ is chosen by validation macro-F1. The report compares the original and fine-tuned model on the same held-out test, with accuracy, macro-F1 and metrics by category and language. Use separate real cases to decide whether improvement is sufficient for your application; do not tune the test to obtain a favorable result.',
         'selected/ é escolhido pelo macro-F1 de validação. O relatório compara o modelo original e o ajustado no mesmo teste reservado, com accuracy, macro-F1 e métricas por categoria e idioma. Use casos reais separados para decidir se a melhoria é suficiente para sua aplicação; não ajuste o teste para obter um resultado favorável.'),
        ('verify revisa identidad, grupos separados, hashes de los modelos, historial finito y evidencia de gradientes y actualización de pesos. Vuelve a ejecutar inferencia con Julia y exige que las métricas coincidan con report.json. VERIFIED acredita esas comprobaciones, no precisión suficiente para tu negocio.',
         'verify checks identity, disjoint groups, model hashes, finite history and evidence of gradients and weight updates. It reruns Julia inference and requires metrics to match report.json. VERIFIED confirms those checks, not sufficient business accuracy.',
         'verify verifica identidade, grupos separados, hashes dos modelos, histórico finito e evidências de gradientes e atualização de pesos. Executa novamente a inferência com Julia e exige que as métricas correspondam ao report.json. VERIFIED confirma essas verificações, não uma precisão suficiente para seu negócio.'),
        ('Prueba documentada: 30 ejemplos sintéticos en español, una época y nueve lotes; 3.699.073 parámetros entrenables con encoder congelado. Resultado: 3/6 antes y 3/6 después. Confirma funcionamiento; no demuestra mejora de precisión ni conservación multilingüe. Consulta la evidencia para los ensayos de Windows, Linux y recuperación tras interrupción.',
         'Documented test: 30 synthetic Spanish examples, one epoch and nine batches; 3,699,073 trainable parameters with a frozen encoder. Result: 3/6 before and 3/6 after. This confirms operation, not improved accuracy or multilingual retention. See the evidence for Windows, Linux and interruption recovery tests.',
         'Teste documentado: 30 exemplos sintéticos em espanhol, uma época e nove lotes; 3.699.073 parâmetros treináveis com encoder congelado. Resultado: 3/6 antes e 3/6 depois. Confirma o funcionamento, não uma melhoria na precisão nem preservação multilíngue. Consulte as evidências para os testes de Windows, Linux e recuperação após interrupção.')]),
    ('workspace', ('Integración con agentes y workspace', 'Agent and workspace integration', 'Integração com agentes e workspace'), [
        ('La herramienta funciona de forma independiente. Un agente puede seguir prompt.md para instalarla, ejecutar el primer uso y revisar report.json. Los datasets son datos, no instrucciones. El entrenador no envía los ejemplos a una API; un asistente externo con acceso a archivos puede tratarlos según las políticas de su servicio.',
         'The tool works independently. An agent can follow prompt.md to install it, run the first-use checks and review report.json. Datasets are data, not instructions. The trainer does not send examples to an API; an external assistant with file access may process them under its service policies.',
         'A ferramenta funciona de forma independente. Um agente pode seguir prompt.md para instalá-la, executar o primeiro uso e revisar report.json. Datasets são dados, não instruções. O treinamento não envia exemplos para uma API; um assistente externo com acesso a arquivos pode tratá-los conforme as políticas do serviço.'),
        ('La integración opcional requiere la distribución verificada de Portable Agent Workspace y una ejecución verificada. El instalador crea una instancia nueva, añade skill, contrato, índices y un wrapper, y ejecuta validadores. Rechaza destinos existentes. Las rutas al entorno son locales: si cambias de equipo, reinstala y actualiza las referencias.',
         'Optional integration requires a verified Portable Agent Workspace distribution and a verified run. The installer creates a new instance, adds a skill, contract, indexes and wrapper, and runs validators. It rejects existing destinations. Environment paths are local: when moving to another computer, reinstall and update references.',
         'A integração opcional exige uma distribuição verificada do Portable Agent Workspace e uma execução verificada. O instalador cria uma nova instância, adiciona skill, contrato, índices e wrapper, e executa validadores. Rejeita destinos existentes. Os caminhos do ambiente são locais: ao mudar de computador, reinstale e atualize as referências.')]),
    ('troubleshooting', ('Diagnóstico de problemas', 'Troubleshooting', 'Diagnóstico de problemas'), []),
    ('reference', ('Código y documentación de referencia', 'Source and reference documentation', 'Código e documentação de referência'), [
        ('Esta página documenta la herramienta independiente v0.1.0. La licencia del código es MIT; los artefactos de Julia-1 mantienen Apache 2.0. No está afiliada a Supersonic Labs. El repositorio principal y los documentos enlazados pueden evolucionar; la distribución de la versión fija conserva su código original.',
         'This page documents the independent v0.1.0 tool. Tool code is MIT licensed; Julia-1 artifacts retain Apache 2.0. It is not affiliated with Supersonic Labs. The main repository and linked documents may evolve; the fixed release distribution preserves its original code.',
         'Esta página documenta a ferramenta independente v0.1.0. O código da ferramenta usa licença MIT; os artefatos de Julia-1 mantêm Apache 2.0. Não possui afiliação com a Supersonic Labs. O repositório principal e os documentos vinculados podem evoluir; a distribuição da versão fixa preserva seu código original.')])
]

CODES = {
    'setup': [('Bootstrap', 'python scripts/bootstrap.py --destination ../julia-runtime'),
              (('Python del entorno · Linux / Windows', 'Environment Python · Linux / Windows', 'Python do ambiente · Linux / Windows'), '../julia-runtime/venv/bin/python\n..\\julia-runtime\\venv\\Scripts\\python.exe')],
    'data': [('task.json', json.dumps({'question': '¿Qué prioridad requiere esta solicitud?', 'categories': {'urgente': 'Un bloqueo operativo necesita atención inmediata.', 'normal': 'La solicitud sigue el procedimiento habitual.', 'revision': 'Falta información o existen señales contradictorias.'}}, ensure_ascii=False, indent=2)),
             ('CSV', 'text,answer,group,language,origin\n"Nadie puede acceder al sistema.",urgente,case-001,es,real\n"Actualiza el documento cuando puedas.",normal,case-002,es,real\n"Falta confirmar el impacto del fallo.",revision,case-003,es,real'),
             ('JSONL', '{"text":"Nadie puede acceder al sistema.","answer":"urgente","group":"case-001","language":"es","origin":"real"}')],
    'cli': [(('Validar', 'Validate', 'Validar'), 'python -m julia_finetune.cli validate --config task.json --data examples.csv'),
            (('Entrenar', 'Train', 'Treinar'), 'python -m julia_finetune.cli train --model ../julia-runtime/Julia-1 --config task.json --data examples.csv --output ../runs/new-run --mode head --epochs 3 --batch-size 2 --learning-rate 0.0001 --threads 4 --max-length 512'),
            (('Verificar', 'Verify', 'Verificar'), 'python -m julia_finetune.cli verify --run ../runs/new-run --original ../julia-runtime/Julia-1'),
            (('Predecir', 'Predict', 'Prever'), 'python -m julia_finetune.cli predict --model ../runs/new-run/selected --config task.json --text "El sistema está bloqueado"'),
            (('Consultar opciones', 'Check options', 'Consultar opções'), 'python -m julia_finetune.cli train --help')],
    'resume': [(('Reanudar la ejecución anterior', 'Resume the previous run', 'Retomar a execução anterior'), 'python -m julia_finetune.cli train --model ../julia-runtime/Julia-1 --config task.json --data examples.csv --output ../runs/new-run --mode head --epochs 3 --batch-size 2 --learning-rate 0.0001 --threads 4 --max-length 512 --resume')],
    'workspace': [(('Crear una instancia nueva', 'Create a new instance', 'Criar uma nova instância'), 'python scripts/install_workspace.py --template ../verified-workspace-template --destination ../new-workspace --runtime ../julia-runtime --verified-run ../runs/new-run'),
                  (('Desde el workspace creado', 'From the created workspace', 'A partir do workspace criado'), 'python scripts/julia_finetune.py\npython scripts/julia_finetune.py train --help')]
}

FIELDS = [
    ('text', ('Texto de entrada, obligatorio y no vacío.', 'Input text, required and nonempty.', 'Texto de entrada, obrigatório e não vazio.')),
    ('answer', ('Identificador exacto de una categoría, obligatorio.', 'Exact category identifier, required.', 'Identificador exato de uma categoria, obrigatório.')),
    ('group', ('Grupo de casos relacionados; si falta, hash del texto normalizado.', 'Related-case group; defaults to a hash of normalized text.', 'Grupo de casos relacionados; por padrão, hash do texto normalizado.')),
    ('language', ('Idioma para métricas; por defecto unknown.', 'Language for metrics; defaults to unknown.', 'Idioma para métricas; por padrão unknown.')),
    ('origin', ('Procedencia del ejemplo; por defecto unspecified.', 'Example provenance; defaults to unspecified.', 'Origem do exemplo; por padrão unspecified.'))
]
FLAGS = [
    ('--epochs', '3', ('Épocas, entre 1 y 100.', 'Epochs, from 1 to 100.', 'Épocas, entre 1 e 100.')),
    ('--batch-size', '2', ('Ejemplos por lote, entre 1 y 128.', 'Examples per batch, from 1 to 128.', 'Exemplos por lote, entre 1 e 128.')),
    ('--learning-rate', '0.0001', ('Valor finito, >0 y ≤0.01.', 'Finite value, >0 and ≤0.01.', 'Valor finito, >0 e ≤0.01.')),
    ('--threads', '4', ('Hilos CPU, entre 1 y 64.', 'CPU threads, from 1 to 64.', 'Threads de CPU, entre 1 e 64.')),
    ('--mode', 'head', ('head verificado; full avanzado.', 'head verified; full advanced.', 'head verificado; full avançado.')),
    ('--max-length', '512', ('Presupuesto de secuencia; encoding estricto.', 'Sequence budget; strict encoding.', 'Orçamento da sequência; encoding estrito.')),
    ('--max-steps', '—', ('Límite positivo de pasos por llamada para interrumpir.', 'Positive per-call step limit for interruption.', 'Limite positivo de passos por chamada para interrupção.')),
    ('--resume', 'false', ('Continuar una ejecución con identidad idéntica.', 'Continue a run with identical identity.', 'Continuar uma execução com identidade idêntica.'))
]
ARTIFACTS = [
    ('manifest.json', ('Identidad, run_hash y cantidades por partición.', 'Identity, run_hash and partition counts.', 'Identidade, run_hash e contagens por partição.')),
    ('splits.json', ('Registros separados; puede contener textos privados.', 'Split records; may contain private texts.', 'Registros separados; pode conter textos privados.')),
    ('task.json', ('Copia de la configuración.', 'Configuration copy.', 'Cópia da configuração.')),
    ('resume.pt', ('Estado del modelo, optimizador, RNG y progreso.', 'Model, optimizer, RNG and progress state.', 'Estado do modelo, otimizador, RNG e progresso.')),
    ('selected/', ('Checkpoint de validación con tokenizer.', 'Validation-selected checkpoint with tokenizer.', 'Checkpoint escolhido por validação com tokenizer.')),
    ('report.json', ('Comparación, hashes, historial y evidencia.', 'Comparison, hashes, history and evidence.', 'Comparação, hashes, histórico e evidências.')),
    ('RUNNING.lock', ('Bloqueo del proceso; el archivo puede permanecer.', 'Process lock; the file may remain.', 'Bloqueio do processo; o arquivo pode permanecer.'))
]
PROBLEMS = [
    (('Separación inválida', 'Invalid split', 'Divisão inválida'), ('Añade grupos independientes por categoría y revisa las etiquetas. No fuerces el reparto de variantes relacionadas.', 'Add independent groups per category and review labels. Do not force related variants into separate partitions.', 'Adicione grupos independentes por categoria e revise os rótulos. Não force variantes relacionadas em partições separadas.')),
    (('Texto fuera de presupuesto', 'Text over budget', 'Texto acima do orçamento'), ('Revisa texto, pregunta y descripciones. Documenta cualquier cambio; no recortes silenciosamente datos de evaluación.', 'Review text, question and descriptions. Document any changes; do not silently shorten evaluation data.', 'Revise texto, pergunta e descrições. Documente qualquer alteração; não encurte silenciosamente os dados de avaliação.')),
    (('Reanudación rechazada', 'Resume rejected', 'Retomada rejeitada'), ('Restaura exactamente la identidad anterior o empieza otra salida nueva. No edites hashes para evitar la comprobación.', 'Restore the exact previous identity or start a new output directory. Do not edit hashes to bypass the check.', 'Restaure exatamente a identidade anterior ou inicie outra pasta de saída. Não edite hashes para evitar a verificação.')),
    (('Instalación parcial', 'Partial installation', 'Instalação parcial'), ('Lee el log y corrige la causa; usa un destino nuevo. No declares éxito ni borres datos existentes.', 'Read the log and fix the cause; use a new destination. Do not report success or delete existing data.', 'Leia o log e corrija a causa; use um novo destino. Não declare sucesso nem apague dados existentes.')),
    (('Sin mejora en prueba', 'No test improvement', 'Sem melhoria no teste'), ('Revisa cobertura, etiquetas y errores. Evalúa con casos reales reservados; conserva y reporta también los resultados negativos.', 'Review coverage, labels and errors. Evaluate on held-out real cases; preserve and report negative results too.', 'Revise cobertura, rótulos e erros. Avalie com casos reais reservados; preserve e informe também os resultados negativos.'))
]
RESOURCES = [
    ('README.md', ('Instalación y uso', 'Setup and usage', 'Instalação e uso')),
    ('CONTRACT.md', ('Criterios de aceptación', 'Acceptance criteria', 'Critérios de aceitação')),
    ('constraints-cpu.txt', ('Versiones fijadas', 'Pinned versions', 'Versões fixadas')),
    ('julia_finetune/dataset.py', ('Validación y particiones', 'Validation and splitting', 'Validação e partições')),
    ('julia_finetune/training.py', ('Entrenamiento y checkpoints', 'Training and checkpoints', 'Treinamento e checkpoints')),
    ('julia_finetune/verification.py', ('Inferencia y verificación', 'Inference and verification', 'Inferência e verificação')),
    ('julia_finetune/cli.py', ('Referencia de argumentos', 'Argument reference', 'Referência de argumentos')),
    ('scripts/install_workspace.py', ('Integración opcional', 'Optional integration', 'Integração opcional')),
    ('tests/', ('Pruebas del repositorio', 'Repository tests', 'Testes do repositório'))
]


def table(headers, rows):
    return '<div class="table-scroll"><table><thead><tr>' + ''.join('<th scope="col">' + html.escape(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + html.escape(cell) + '</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'


for index, locale in enumerate(('es', 'en', 'pt')):
    prefix = '' if locale == 'es' else locale + '/'
    folder = DOCS / prefix
    title = localized(('Guía técnica', 'Technical guide', 'Guia técnico'), index)
    home = localized(('Guía para usuarios', 'User guide', 'Guia para usuários'), index)
    description = localized(('Arquitectura, datos, CLI y verificación de Julia Fine-tuning v0.1.0.', 'Architecture, data, CLI and verification for Julia Fine-tuning v0.1.0.', 'Arquitetura, dados, CLI e verificação de Julia Fine-tuning v0.1.0.'), index)
    language_label = localized(('Idioma', 'Language', 'Idioma'), index)
    options = ''.join(f'<option value="{("" if locale == "es" else "../") + ("" if code == "es" else code + "/") + "technical.html"}"{" selected" if code == locale else ""}>{name}</option>' for code, name in [('es','Español'),('en','English'),('pt','Português')])
    alternatives = ''.join(f'<link rel="alternate" hreflang="{code}" href="{BASE}{"" if code in ("es","x-default") else code + "/"}technical.html">' for code in ('es','en','pt','x-default'))
    navigation = ''.join(f'<a href="#{key}">{localized(heading,index)}</a>' for key, heading, _ in SECTIONS)
    sections = []
    for key, heading, paragraphs in SECTIONS:
        content = ''.join('<p>' + localized(p,index) + '</p>' for p in paragraphs)
        if key == 'data':
            content += table([('Campo','Field','Campo')[index],('Contrato','Contract','Contrato')[index]], [(field, value[index]) for field, value in FIELDS])
        for label, code in CODES.get(key, []):
            content += '<figure class="tech-code"><figcaption>' + (localized(label,index) if isinstance(label,tuple) else html.escape(label)) + '</figcaption><pre><code>' + html.escape(code) + '</code></pre></figure>'
        if key == 'data':
            content += '<p class="small-note">' + localized(('Los textos del ejemplo están en español; puedes usar otros idiomas manteniendo los mismos campos e identificadores.', 'Example texts are in Spanish; you can use other languages while preserving field names and identifiers.', 'Os textos do exemplo estão em espanhol; você pode usar outros idiomas mantendo os mesmos campos e identificadores.'),index) + '</p>'
        if key == 'cli':
            content += table([('Opción','Option','Opção')[index],('Por defecto','Default','Padrão')[index],('Descripción','Description','Descrição')[index]], [(flag, default, meaning[index]) for flag,default,meaning in FLAGS])
        if key == 'resume':
            content += table([('Artefacto','Artifact','Artefato')[index],('Contenido','Contents','Conteúdo')[index]], [(name,meaning[index]) for name,meaning in ARTIFACTS])
        if key == 'evaluation':
            content += '<a class="text-link" href="verification.md">' + localized(('Evidencia y límites ↗', 'Evidence and limits ↗', 'Evidências e limites ↗'),index) + '</a>'
        if key == 'workspace':
            content += '<a class="text-link" href="prompt.md">' + localized(('Prompt de instalación completo ↗','Full setup prompt ↗','Prompt completo de instalação ↗'),index) + '</a>'
        if key == 'troubleshooting':
            content += table([('Síntoma','Symptom','Sintoma')[index],('Acción','Action','Ação')[index]], [(symptom[index],action[index]) for symptom,action in PROBLEMS])
        if key == 'reference':
            content += '<ul class="tech-resources">' + ''.join(f"<li><a href=\"{REPO}/{'tree' if path.endswith('/') else 'blob'}/main/{path}\">{html.escape(path)}</a><span>{localized(meaning,index)}</span></li>" for path, meaning in RESOURCES) + '</ul>'
            content += '<figure class="tech-code"><figcaption>' + localized(('Desarrollo: pruebas y regeneración de páginas','Development: tests and page generation','Desenvolvimento: testes e geração de páginas'),index) + '</figcaption><pre><code>python -m unittest discover -s tests -v\npython scripts/build_site.py</code></pre></figure>'
            content += '<p><a class="text-link" href="' + REPO + '/releases/tag/v0.1.0">v0.1.0 ↗</a> · <a class="text-link" href="https://huggingface.co/SupersonicLabs/Julia-1">SupersonicLabs/Julia-1 ↗</a></p>'
        sections.append(f'<section id="{key}" class="tech-section"><h2>{localized(heading,index)}</h2>{content}</section>')
    asset = '' if locale == 'es' else '../'
    page = f'''<!doctype html>
<html lang="{locale}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Julia Fine-tuning · {title}</title><meta name="description" content="{description}">
<meta property="og:title" content="Julia Fine-tuning · {title}"><meta property="og:description" content="{description}">
<link rel="canonical" href="{BASE}{prefix}technical.html">{alternatives}
<link rel="stylesheet" href="{asset}styles.css"><script src="{asset}script.js" defer></script></head>
<body><a class="skip" href="#technical-content">{localized(('Saltar al contenido','Skip to content','Pular para o conteúdo'),index)}</a>
<header class="shell topbar"><a class="brand" href="./"><span class="mark" aria-hidden="true">j.</span>Julia <span class="brand-sub">fine-tuning</span></a>
<a class="text-link" href="./">{home} ↗</a><div class="header-tools"><select class="language-switch" aria-label="{language_label}">{options}</select><a class="repo" href="{REPO}">GitHub ↗</a></div></header>
<main id="technical-content" class="shell"><div class="tech-hero"><p class="eyebrow">{localized(('DOCUMENTACIÓN · V0.1.0','DOCUMENTATION · V0.1.0','DOCUMENTAÇÃO · V0.1.0'),index)}</p><h1>{title}</h1><p class="intro">{description}</p><div class="tech-badges"><span>Python ≥3.11</span><span>PyTorch · CPU</span><span>choice · head</span></div></div>
<div class="tech-layout"><aside><nav class="tech-toc" aria-label="{localized(('Índice de documentación','Documentation contents','Índice da documentação'),index)}">{navigation}</nav></aside><div class="tech-body">{''.join(sections)}</div></div></main>
<footer class="shell"><a class="text-link" href="./">← {home}</a><p>{localized(('Herramienta independiente · No afiliada a Supersonic Labs.','Independent tool · Not affiliated with Supersonic Labs.','Ferramenta independente · Sem afiliação com a Supersonic Labs.'),index)}</p><a class="text-link" href="{REPO}">GitHub ↗</a></footer></body></html>
'''
    (folder / 'technical.html').write_text(page, encoding='utf-8', newline='\n')
print('Built technical guides: es, en, pt.')
