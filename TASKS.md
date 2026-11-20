# Tareas — Asistente energético

Actualizado: 20-11-2026.

Asistente público para ayudar a hogares a entender su consumo eléctrico y
comparar decisiones con datos y supuestos explícitos. Proyecto de portfolio y
aprendizaje de datos de energía e IA, con motor Python y web Django.
Trabajamos al ritmo de Aitor, una tarea cada vez, explicando qué hacemos y por qué.
Aitor ejecuta los pasos y escribe el código con ayuda. El asistente solo modifica
archivos cuando Aitor lo pide expresamente, como esta lista.
Crear commits únicamente cuando Aitor lo autorice expresamente.

Marcar `[x]` únicamente cuando el resultado esté comprobado. Mantener pendientes
las tareas que solo estén propuestas. Actualizar esta lista conforme avancemos.

La prioridad vigente es publicar el planificador actual, incorporar análisis de
consumos reales, conectar el chat a los servicios comprobados y ampliar después
hacia autoconsumo. La simulación solar queda como idea posterior. README describe
el objetivo y el alcance de la primera entrega; docs/decisiones.md conserva sus motivos.

## 1. Preparar el entorno y el repositorio

- [x] Comprobar que Git está instalado.
- [x] Crear y activar el entorno virtual `.venv`.
- [x] Verificar el intérprete y que el entorno virtual esté activo (confirmado por Aitor).
- [x] Crear esta lista de tareas.
- [x] Instalar y comprobar uv en la terminal de Aitor (confirmado por Aitor).
- [x] Instalar uv fuera de `.venv` para poder usar `uv sync`.
- [x] Revisar la relación entre Python, `.venv`, uv, `pyproject.toml` y `uv.lock`.
- [x] Inicializar el repositorio Git y comprobar su estado.
- [x] Crear y revisar `.gitignore`: entorno, cachés, secretos y documentos de `_local/`.
- [x] Preparar `pyproject.toml` con compatibilidad Python >=3.12.
- [x] Comprobar la ejecución con `uv run` y generar `uv.lock`.
- [x] Crear un README breve con objetivo y pasos para ejecutar el proyecto.
- [x] Registrar las decisiones técnicas en `docs/decisiones.md`.
- [x] Revisar los archivos y hacer el primer commit local.
- [x] Mover esta lista de `_local/` a la raíz para incluirla en el historial de Git.

## 2. Primer motor con datos ficticios

Objetivo: una función devuelve las dos horas consecutivas más baratas dentro
del horario indicado, con un ejemplo verificable a mano.

- [x] Definir entradas y salida: precios en €/kWh como Decimal, horario y tupla (hora, coste).
- [x] Acordar el horario [inicio, fin) y resolver empates eligiendo la primera franja.
- [x] Preparar una tabla pequeña de precios ficticios.
- [x] Calcular a mano las parejas: 0,32 €, 0,20 € y 0,23 € entre las 18 y las 22.
- [x] Escribir `buscar_mejor_franja`, independiente de Django y de internet.
- [x] Ejecutar la función y comprobar el resultado ficticio: 19–21, 0,20 € a 1 kW.
- [x] Comprobar que elige horas consecutivas y respeta el horario solicitado.
- [x] Rechazar precios ausentes y horarios demasiado cortos; comprobar los empates.
- [ ] Añadir pruebas de los límites del horario: fuera de 0–24, invertido y fin a las 24.
- [x] Añadir seis pruebas automáticas del motor.
- [x] Separar el ejemplo ejecutable de la importación mediante `if __name__ == "__main__"`.
- [x] Registrar en docstrings y README el consumo constante de 1 kW y los límites del ejemplo.
- [ ] Aitor explica el algoritmo con palabras propias como repaso de aprendizaje.
- [x] Guardar el motor y la documentación en commits locales.

## 3. Incorporar datos reales

- [x] Elegir REData de Red Eléctrica y comprobar acceso HTTP 200 al PVPC peninsular.
- [ ] Revisar las condiciones de uso y atribución antes de publicar los datos en la web.
- [x] Revisar el JSON: `included`, serie PVPC ID 1001, registros `value` y `datetime`.
- [x] Revisar la muestra del 15-11-2026: 24 horas consecutivas con desplazamiento +01:00.
- [x] Convertir de €/MWh a €/kWh mediante Decimal y división entre 1.000.
- [x] Separar consulta (`obtener_precios`), adaptación (`convertir_precios`) y cálculo.
- [x] Evitar peticiones HTTP al importar `consultar_precios.py`.
- [x] Validar la fecha completa de cada registro frente al día solicitado.
- [x] Rechazar registros con minutos, segundos o microsegundos distintos de cero.
- [x] Rechazar horas repetidas, incluso con desplazamientos horarios distintos.
- [x] Propagar errores HTTP y tiempos de espera agotados a quien llama a la consulta.
- [x] Probar la conversión con muestras locales, sin depender de internet.
- [x] Verificar a mano el resultado real entre 18 y 22: 20–22, 0,44651 € a 1 kW.
- [x] Añadir siete pruebas del adaptador y cuatro de consulta HTTP simulada.
- [x] Ejecutar las 17 pruebas del proyecto: todas correctas, sin conexión a la API.
- [x] Guardar la integración de precios reales en el commit `5da5905`.
- [x] Actualizar el README con la consulta real, su ejecución y sus limitaciones actuales.
- [x] Normalizar cada instante a Europe/Madrid antes de comprobar fecha, hora y duplicados.
- [x] Exigir desplazamiento UTC explícito y probar invierno, verano y cambios de fecha entre zonas.
- [x] Declarar tzdata como dependencia directa para disponer de zonas IANA también en Windows.
- [x] Definir el rechazo explícito de días con cambio de hora y horarios que crucen medianoche en esta versión.
- [x] Rechazar precios ausentes, no numéricos, booleanos, NaN e infinitos en el adaptador, conservando cero y negativos.
- [x] Probar la precisión de enteros y Decimal y el error web con una respuesta HTTP de precios inválidos.
- [x] Validar la estructura utilizada: objeto raíz, included, ID de serie, attributes y lista no vacía de values.
- [x] Rechazar registros de tipo inesperado o sin datetime textual ISO con separador T y hora válida.
- [x] Probar cuerpos vacíos, HTML, JSON truncado y errores de estructura desde servicios y web.
- [x] Definir caducidad de la copia local: cinco minutos desde la descarga, mostrando error si falla la actualización tras vencer.
- [ ] Revisar la antigüedad de la publicación de la fuente, distinta de la caducidad de nuestra caché.

## 4. Construir y publicar el planificador Django

- [x] Definir la primera pantalla: fecha y horas de inicio y fin dentro del mismo día.
- [x] Instalar Django 6.1.3, crear `config` y comprobar el arranque local con Aitor.
- [x] Crear y registrar la aplicación `energia` y sus rutas.
- [x] Crear el formulario GET y conectarlo con la consulta y el motor.
- [x] Mostrar franja recomendada, unidades, fuente, fecha y mensajes de error.
- [x] Añadir tres pruebas web: entrada vacía, resultado correcto y horario corto sin consulta.
- [x] Completar docstrings en los módulos, clases y funciones Python existentes.
- [x] Agrupar cálculo y consulta en `energia/servicios/`, y todas las pruebas en `energia/tests/`.
- [x] Actualizar imports, rutas de patch y comandos después de mover archivos.
- [x] Ejecutar las 20 pruebas sin red y el ejemplo ficticio después de la reorganización.
- [x] Reutilizar días completos por fecha en una caché en memoria de Django con duración configurable.
- [x] Mantener la caché en la capa web y los servicios independientes de Django.
- [x] Evitar guardar errores y datos parciales; reconsultar al caducar sin servir la copia vencida.
- [x] Probar el recorrido completo con precios simulados: formulario → cálculo → resultado.
- [x] Probar mensajes, conservación de campos y ausencia de recomendación ante fallos HTTP, ValueError y precios vacíos o incompletos.
- [x] Comprobar que una búsqueda correcta después de un fallo muestra el resultado y elimina el error.
- [x] Ejecutar las 24 pruebas sin red: siete del recorrido web y 17 de servicios.
- [x] Ejecutar las 29 pruebas sin red después de validar precios: once del adaptador y ocho de web.
- [x] Ejecutar las 40 pruebas sin red después de validar estructuras: quince del adaptador, diez de consulta y nueve de web.
- [x] Configurar TIME_ZONE en Europe/Madrid y mostrar la zona y la limitación de cambios de hora en el formulario.
- [x] Ejecutar las 51 pruebas sin red tras normalizar: veintidós del adaptador, once de consulta y doce de web.
- [x] Ejecutar las 59 pruebas: reutilización entre horarios, caducidad sin esperas y recuperación tras respuestas parciales.
- [x] Mejorar la presentación del formulario y del resultado con una interfaz adaptable a móvil.
- [x] Mostrar selectores horarios legibles y convertir las opciones a enteros para el motor.
- [x] Mostrar una tabla del horario solicitado con los dos intervalos elegidos destacados.
- [x] Presentar importes en español, referencia de 1 kW y estados inicial y de error sin precios ficticios.
- [x] Comprobar 64 pruebas y que Django encuentre `energia/estilos.css`.
- [x] Revisar capturas locales de escritorio y móvil a 320 y 390 píxeles, sin desbordamiento horizontal.
### Repositorio remoto, ramas y pruebas automáticas

Plataforma elegida: GitHub para alojar el código, revisar pull requests y ejecutar
las pruebas con GitHub Actions. El remoto `origin` apunta a
https://github.com/aiveni/asistente-energetico.git y `main` sigue a `origin/main`.

Durante la preparación de la primera publicación trabajaremos directamente en
`development`, con cambios pequeños y comprobados. `main` recogerá avances
estables después de revisarlos y comprobar las pruebas aplicables. Tras publicar,
practicaremos ramas `feature/...` y pull requests para revisar cada tarea.
Las ramas no crean por sí solas servidores ni publican la web. `main` y
`development` ya existen localmente; el seguimiento remoto de `development`
queda pendiente.

- [x] Elegir GitHub, conectar el repositorio remoto y realizar el primer push de `main` (seguimiento de `origin/main` comprobado).
- [ ] Guardar la documentación pendiente en `development` y subirla a GitHub; el objetivo y alcance ya están en `e3ca322`. **Siguiente paso guiado.**
- [x] Documentar el flujo inicial: trabajo directo en `development`, comprobaciones y promoción de avances estables a `main`.
- [x] Crear `development` desde `main` (comprobado: ambas parten de `e3ca322`).
- [ ] Promover la documentación revisada de `development` a `main`, subir ambas ramas y comprobar su seguimiento remoto.
- [ ] Configurar las pruebas automáticas en GitHub Actions para los cambios y pull requests hacia `development` y `main`.
- [ ] Comprobar el flujo inicial con CI: desarrollar en `development`, revisar las pruebas y promover un avance estable a `main`.

El siguiente cambio técnico será configurar CI directamente en `development`.

### Gestión por tareas después de la primera publicación

- [ ] Practicar una rama `feature/...` desde `development` y una pull request hacia `development`, con descripción, revisión y pruebas correctas antes de fusionar.
- [ ] Configurar la protección de `main` y `development` con pull requests y comprobaciones obligatorias, según las opciones de la cuenta y el trabajo individual.
- [ ] Practicar la promoción de `development` a `main` mediante pull request para preparar una versión publicable.

### Publicación en la nube

El repositorio remoto aloja el código y su historial. El alojamiento de la web
ejecutará Django y ofrecerá la URL pública. La publicación se hará desde una
versión comprobada de `main`. Un servidor adicional de pruebas para `development`
se valorará más adelante, sin dar por hecho ese coste.

Destino propuesto: Google Cloud Run para ejecutar Django. Antes del despliegue
se revisarán la cuenta de facturación, los costes de ejecución, construcción y
almacenamiento de imágenes, y las alertas de gasto. El tramo gratuito no garantiza
que el conjunto del despliegue tenga coste cero. La elección sigue pendiente.
Referencia: [precios de Cloud Run](https://cloud.google.com/run/pricing).

- [ ] Preparar la configuración de producción: secretos, DEBUG, hosts y HTTPS.
- [ ] Elegir alojamiento, revisar costes y decidir el despliegue con Aitor.
- [ ] Elegir un backend de caché compartido si el despliegue utiliza varios procesos.
- [ ] Preparar los archivos estáticos, el servidor de aplicación y los comandos de arranque para el alojamiento elegido.
- [ ] Definir cómo desplegar una versión de `main` y cómo volver a la anterior si falla.
- [ ] Publicar y comprobar que el planificador funciona desde fuera del equipo.
- [ ] Añadir enlace, captura, instrucciones y decisiones al portfolio.

## 5. Analizar consumos reales después del planificador público

Recorrido previsto: subir un archivo admitido, indicar una tarifa compatible,
revisar consumos y costes, definir un cambio posible y comparar escenarios bajo
los mismos supuestos. El análisis se comprobará antes de incorporarlo al chat.

- [ ] Concretar el primer caso de uso con hogares y el resultado que necesitan comprender o decidir.
- [ ] Elegir un primer formato de archivo y tipo de tarifa admitidos; documentar columnas, unidades, intervalos y datos necesarios para el coste.
- [ ] Preparar un archivo sintético pequeño, su resultado manual y una muestra real anonimizada para contrastar la importación.
- [ ] Definir el tratamiento mínimo del archivo: límites de tamaño y tipo, validación del contenido, retención o borrado y exclusión de identificadores de las muestras y registros.
- [ ] Importar y normalizar fecha, zona horaria y energía por intervalo; detectar ausencias, duplicados y cambios de hora según el soporte definido.
- [ ] Mostrar consumo total, distribución por horas y días, periodos de mayor consumo y cobertura de los datos.
- [ ] Definir la tarifa y obtener los precios aplicables a las mismas fechas e intervalos; mostrar qué conceptos de factura se incluyen en la estimación.
- [ ] Pedir al usuario qué energía puede desplazar y con qué disponibilidad y límites; no deducir los aparatos desplazables solo de la curva agregada.
- [ ] Comparar el caso base con un escenario confirmado, conservando la energía total y mostrando diferencia de coste, restricciones y supuestos.
- [ ] Probar importación, resúmenes y escenarios con resultados verificables y errores de datos controlados.
- [ ] Revisar el recorrido con usuarios y comprobar que entienden el resultado y sus límites antes de ampliar el alcance.

## 6. Añadir el chat sobre los servicios comprobados

El chat se incorporará después de publicar el planificador y validar los servicios
de análisis que utilizará. Podrá explicar resultados y solicitar cálculos con
datos del usuario. RAG, LangChain y LangGraph se contemplan como ampliaciones a
evaluar, sin decidir todavía su adopción ni añadir dependencias por adelantado.
El proveedor del modelo sigue pendiente de elección.

### Primera versión: chat con function calling

- [ ] Definir qué aporta el chat y qué preguntas atenderá.
- [ ] Elegir la integración y revisar costes y gestión de claves.
- [ ] Diseñar una herramienta para planificar una franja a partir de fecha, inicio y fin, reutilizando consulta, validación y motor.
- [ ] Implementar function calling: el modelo solicita la herramienta; el backend valida sus argumentos, ejecuta Python y devuelve el resultado para redactar la respuesta.
- [ ] Mantener precios y cálculos en los servicios comprobados, con fecha, zona horaria y unidades explícitas en el resultado de la herramienta.
- [ ] Exponer herramientas para consultar el resumen del consumo y comparar escenarios confirmados; decidir qué datos mínimos recibirá el modelo.
- [ ] Definir respuestas ante datos ausentes y peticiones fuera de alcance.
- [ ] Probar argumentos inválidos, fallos de consulta y fidelidad de la respuesta al resultado de la herramienta.
- [ ] Evaluar respuestas y añadir límites de uso, tiempo y llamadas a herramientas antes de publicarlo.

### Ampliación posible: RAG documental

RAG recuperaría fragmentos relevantes de documentos y los aportaría al modelo
para responder preguntas explicativas. Los precios horarios se seguirán
consultando mediante las herramientas del motor.

- [ ] Definir preguntas que necesiten documentación energética y decidir si aportan valor al alcance del asistente.
- [ ] Seleccionar un corpus pequeño de fuentes fiables, con procedencia, fecha y condiciones de uso revisadas.
- [ ] Si se incorpora RAG, preparar recuperación y respuestas con citas; comparar búsqueda sencilla y embeddings según las necesidades del corpus.
- [ ] Evaluar relevancia de los fragmentos, correspondencia de las citas y respuestas cuando no haya información suficiente.

### Evaluación posterior de LangChain y LangGraph

Function calling y RAG se pueden implementar sin estos frameworks. Se valorarán
tanto por lo que aporten al proyecto como por su utilidad para el aprendizaje,
documentando el coste de mantener la solución elegida.

- [ ] Comparar una integración directa con el SDK del proveedor y un prototipo con LangChain para el mismo caso de uso, revisando claridad, dependencias y facilidad de prueba.
- [ ] Valorar un prototipo con LangGraph si necesitamos controlar varios pasos, decisiones, estado o reanudación de una ejecución; no presupone usar varios agentes.
- [ ] Registrar qué se adopta y por qué, manteniendo el motor independiente del modelo y de los frameworks.

## 7. Ampliaciones funcionales del asistente energético

Visión futura para concretar después de publicar el primer planificador y añadir
su chat. Estas capacidades quedan como trabajo pendiente. La primera versión
mantiene el alcance comprobado: dos horas consecutivas de un mismo día, con
precios PVPC y un coste de referencia para 1 kW constante.

| Capacidad | Alcance actual y evolución prevista |
| --- | --- |
| Planificar consumos | Ya se calculan dos horas; ampliar a duraciones configurables y fechas y horas límite. |
| Analizar consumos reales | Siguiente ampliación prioritaria tras publicar: importar consumos, revisar patrones y definir escenarios con el usuario. |
| Estimar y comparar costes | Existe el coste de referencia a 1 kW; falta incorporar el consumo del aparato y comparar escenarios. |
| Resolver dudas sobre autoconsumo | Ampliación del chat documental, con fuentes oficiales, citas y fecha de revisión. |
| Estimar producción solar y simular escenarios | Idea posterior: definir datos de entrada, fuente de producción y método de comparación con el consumo. |

### Planificar duraciones y horas límite

- [ ] Generalizar el motor a una duración configurable y comprobar a mano una franja de tres horas, conservando el comportamiento actual de dos horas.
- [ ] Definir fecha y hora de disponibilidad y fecha y hora límite para casos como cargar el coche tres horas antes de las siete, incluyendo horarios que atraviesen medianoche.
- [ ] Consultar los días necesarios, exigir precios disponibles para el horario y documentar los límites de zona horaria y cambios de hora antes de ampliar su soporte.
- [ ] Adaptar formulario y herramienta del chat al nuevo contrato y comprobar duración, límites, empates y datos incompletos.

### Estimar y comparar costes de consumo

- [ ] Definir los datos del aparato: potencia constante o perfil de energía por intervalo, con unidades y supuestos explícitos; no inventar su consumo.
- [ ] Calcular el coste de dos horarios para el mismo consumo y mostrar su diferencia, aclarando qué conceptos se incluyen y cuáles quedarían fuera de una factura completa.
- [ ] Validar la comparación con un ejemplo manual y comunicar cuándo faltan precios o datos del aparato para estimarla.

### Resolver dudas sobre autoconsumo

- [ ] Concretar el caso de RAG del bloque 6 con documentación oficial de IDAE y MITECO, incluida la compensación de excedentes, y revisar su vigencia y condiciones de uso.
- [ ] Evaluar respuestas con citas que apoyen cada explicación, fecha de revisión y petición de datos adicionales cuando la respuesta dependa del contrato o de la instalación.
- [ ] Si se dispone de producción y consumo compatibles, concretar un escenario de autoconsumo y documentar sus periodos, tarifa, balance y supuestos.

Fuentes candidatas: [guías de IDAE](https://www.idae.es/tecnologias/energias-renovables/oficina-de-autoconsumo/guias-tecnicas-sobre-autoconsumo)
y [preguntas frecuentes de MITECO](https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/autoconsumo-electrico/preguntas-frecuentes-autoconsumo.html).

### Estimar producción solar y simular escenarios

- [ ] Concretar el objetivo y las entradas: ubicación, potencia instalada, orientación, inclinación, pérdidas y, para compararla con el consumo, un perfil de demanda.
- [ ] Evaluar PVGIS como fuente de estimaciones de producción y distinguir una estimación basada en datos históricos de una predicción meteorológica para mañana.
- [ ] Comparar generación y consumo en intervalos temporales compatibles, mostrando autoconsumo, excedentes y energía de red con sus supuestos y limitaciones.
- [ ] Contrastar un escenario sencillo antes de conectar la simulación como herramienta del chat.

Fuente candidata: [PVGIS del Joint Research Centre](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en).

Las estimaciones y comparaciones se implementarán en servicios Python comprobables.
El chat podrá solicitar esos cálculos mediante function calling y explicar sus
resultados; las explicaciones documentales se apoyarán en las fuentes del RAG.

## Más adelante

- [ ] Valorar skills propias si aparecen procedimientos que repetimos a menudo.
- [ ] Priorizar y concretar las ampliaciones del bloque 7 después de completar el primer alcance.
- [ ] Dar soporte completo a días de 23 o 25 horas con intervalos y duración real, si se amplía el alcance.
- [ ] Retomar el asistente del paro únicamente cuando se decida expresamente.

## Tareas necesarias añadidas y qué resuelven

- **Objetivo y alcance por entrega:** permiten decidir qué aporta cada ampliación
  y comprobar cuándo termina la primera publicación.
- **Análisis de consumos reales:** conecta la planificación con los datos del hogar
  y permite comparar decisiones sobre una base de consumo y tarifa explícita.
- **Escenarios confirmados por el usuario:** evitan confundir un patrón observado
  con energía que realmente puede cambiar de horario.
- **Validación y tratamiento de archivos:** permiten trabajar con consumos del hogar
  con datos utilizables, límites de carga y una retención definida.
- **Comprobación con usuarios:** permite revisar la utilidad y comprensión de cada
  entrega antes de invertir en nuevas capacidades.
- **Duración y hora límite configurables:** permiten pasar del ejemplo de dos horas
  a consumos como una carga de tres horas que debe terminar antes de una fecha y hora.
- **Modelo de consumo del aparato:** permite estimar y comparar costes con datos
  del caso concreto, más allá de la referencia actual de 1 kW.
- **Autoconsumo con fuentes oficiales:** concreta un uso del RAG que puede evaluarse
  y mantenerse conforme cambie la documentación aplicable.
- **Simulación solar con entradas explícitas:** permite estudiar producción y
  aprovechamiento energético con supuestos revisables antes de ampliar el chat.
- **Function calling para el chat:** permite transformar una petición en lenguaje
  natural en una llamada validada al cálculo Python y explicar su resultado.
- **Evaluación de RAG:** permite decidir si las respuestas necesitan documentación
  recuperada y comprobar que las citas apoyan lo que se responde.
- **Evaluación de frameworks:** permite aprender LangChain y LangGraph con un caso
  concreto y justificar su adopción frente a una integración directa.
- **Repositorio remoto:** permite conservar una copia en GitHub y ejecutar las
  comprobaciones automáticas allí. La conexión de `origin` y el seguimiento de
  `main` a `origin/main` están comprobados.
- **Ramas y revisión de cambios:** durante el arranque permiten trabajar en
  `development` y conservar avances estables en `main`. Las ramas por tarea y
  pull requests se practicarán después de la primera publicación.
- **Archivos estáticos y arranque de producción:** hacen que el alojamiento pueda
  servir la interfaz y ejecutar Django fuera del servidor local de desarrollo.
- **Despliegue y vuelta a la versión anterior:** relacionan lo publicado con un
  commit conocido y permiten recuperar la web si una actualización falla.
- **Tabla de precios y selección visible:** permite comprobar la recomendación
  con los precios del horario elegido, sin confundirlos con otras horas del día.
- **Selectores horarios y estados de pantalla:** facilitan una entrada válida y
  mantienen las explicaciones y los campos cuando la búsqueda no se puede resolver.

- **Caché de días completos:** reduce descargas repetidas y permite recuperar datos
  parciales en la siguiente petición. El plazo máximo evita reutilizar la copia indefinidamente.
- **Backend compartido para producción:** permite que varios procesos del servidor
  reutilicen los mismos precios; la memoria local de desarrollo no se comparte.

- **Contrato del cálculo y casos límite:** evitan resultados ambiguos o recomendaciones
  hechas con datos insuficientes.
- **Unidades y tiempo en datos reales:** evitan confundir precios, intervalos y días
  al pasar del ejemplo ficticio a una fuente real.
- **Pruebas automáticas:** permiten detectar si un cambio rompe un cálculo ya comprobado.
- **Contexto y decisiones versionados:** permiten retomar el proyecto y explicar sus motivos;
  no hace falta construir un sistema de skills para empezar.
- **Configuración de producción y comprobaciones automáticas:** ayudan a mantener
  la web pública y detectar errores antes de publicar cambios.
- **Validación de fecha y hora exacta en el adaptador:** evita mezclar días o convertir
  un registro de las 18:15 en un precio de la hora completa de las 18.
- **Zona horaria:** normalizar antes de extraer la hora evita interpretar UTC como
  hora peninsular o usar precios de otro día local. Exigir desplazamiento evita
  depender de la zona configurada en el equipo.
- **Rechazo de días con cambio de hora:** protege el modelo actual de horas 0–23
  frente a horas inexistentes o repetidas; el soporte completo queda aplazado.
- **Validación de estructura:** transforma los campos ausentes y tipos inesperados
  en errores de datos controlados antes de acceder a ellos o calcular precios.
- **Precios numéricos y finitos:** impide que un valor ausente, un booleano, NaN o
  un infinito llegue al motor y genere un error de servidor o una recomendación incorrecta.
- **Versionar esta lista fuera de `_local/`:** permite revisar el progreso en Git sin
  incluir los otros documentos locales.
- **Servicios y pruebas agrupados en la app:** reducen los archivos sueltos de la raíz
  y permiten encontrar cálculo, consulta y pruebas sin mezclar sus responsabilidades.
- **Pruebas web de errores:** comprueban que los fallos de datos o conexión se explican
  a quien usa el formulario y no se presentan como una recomendación válida.

## Registro de avances

- **16-11-2026:** Aitor confirma la comprobación de Python dentro del entorno virtual.
  Se crea esta lista.
- **16-11-2026:** Entorno con uv preparado, Git inicializado y motor ficticio probado.
  Primer commit: `cc4b9fd`; README inicial: `b63ff2e`.
- **16-11-2026:** Consulta real, adaptador y pruebas guardados en `5da5905`.
  Las 17 pruebas pasan. La muestra del día 15 devuelve 20–22 por 0,44651 € a 1 kW
  dentro del horario 18–22. El soporte general de zonas y cambios de hora sigue pendiente.
- **16-11-2026:** Lista actualizada y trasladada a `TASKS.md` para versionarla.
  Próximo bloque de aprendizaje: arranque local de Django; publicación y chat pendientes.
- **17-11-2026:** Web local creada con aplicación `energia`, formulario GET y plantilla.
  Al revisar los archivos, `energia/tests.py` todavía contenía la plantilla vacía;
  se incorporaron las tres pruebas web acordadas. Las 20 pruebas pasan.
- **17-11-2026:** Docstrings completados y cambios de la web guardados en `0862567`.
  Servicios y pruebas reorganizados en `985c15d`, conservando el ejemplo ficticio
  y el resultado real de muestra. README, decisiones y tareas actualizados.
  Publicación y chat siguen pendientes.
- **17-11-2026:** Añadidas cuatro pruebas web con casos de conexión, timeout,
  HTTP 503, errores de datos, precios vacíos o incompletos y reintento correcto.
  Las 24 pruebas pasan sin internet. La vista ya gestionaba estos casos, por lo
  que se conserva su lógica. Próximo paso: validar los precios recibidos.
- **17-11-2026:** Validación de precios añadida al adaptador. Una prueba nueva
  reprodujo la aceptación indebida de NaN; después de corregirla, las 29 pruebas
  pasan. Se comprueba también el recorrido HTTP → adaptador → web sin internet.
  Pendiente la validación general de la estructura JSON y de la zona horaria.
- **17-11-2026:** Validación de estructuras añadida a consulta y adaptador. La
  prueba inicial reprodujo un TypeError al recibir null como raíz del JSON.
  Tras añadir comprobaciones explícitas, las 40 pruebas pasan sin internet.
  Se actualiza la documentación y se dejan los cambios sin commit por petición
  de Aitor. Próximo paso: normalización y validación de zona horaria.
- **17-11-2026:** Con autorización de Aitor se guarda la validación JSON en
  `8c26c10`. Se normalizan los registros a Europe/Madrid con ZoneInfo y astimezone,
  se exige desplazamiento UTC y se rechazan días con cambio de hora. Se declara
  tzdata como dependencia directa y se alinea Django y el formulario con la zona.
  Las 51 pruebas pasan. La normalización queda sin commit para revisión.
- **17-11-2026:** Normalización guardada con autorización en `b8381b8`. Se añade
  `energia/cache_precios.py`, se integra en la vista y se configura LocMemCache
  con duración inicial de cinco minutos. Se guardan solo días completos y se
  mantienen los servicios sin dependencia de Django. Las 59 pruebas pasan;
  el reloj se simula para comprobar la caducidad. Cambios de caché sin commit.
- **17-11-2026:** Caché guardada con autorización en `96d3686`. Se prepara la
  interfaz con formulario, recomendación destacada, tabla de precios y estados
  inicial y de error. Se añaden selectores horarios y formato español. Las 64
  pruebas pasan; el CSS se descubre correctamente. Revisadas capturas de HTML
  renderizado con datos de prueba en escritorio y móvil, sin desbordamiento de
  página a 320 y 390 píxeles. Cambios de interfaz sin commit para revisión.
- **17-11-2026:** Aitor autoriza el commit de la interfaz. Se vuelven a ejecutar
  las 64 pruebas y todas pasan. Se comprueba que Git no tiene remoto configurado;
  se añade su conexión como paso previo a GitHub Actions.
- **17-11-2026:** Interfaz guardada con autorización en `a0eef81`. A petición
  de Aitor se detallan las tareas de remoto, ramas `main`/`development`/`feature/...`,
  PR/MR, pruebas y publicación en la nube. Se contempla GitLab como alternativa
  a GitHub. Se comprueba que solo existe `main` local y que no hay remoto;
  las nuevas tareas quedan pendientes, sin crear ramas ni desplegar todavía.
- **19-11-2026:** Se detalla la evolución del chat: primera versión con function
  calling sobre los servicios existentes, evaluación de RAG documental y posibles
  prototipos de LangChain y LangGraph. Las ampliaciones y la elección del proveedor
  quedan pendientes; se conserva el orden de publicar primero el planificador.
- **19-11-2026:** Se recoge la visión futura de planificación con duración y hora
  límite, comparación de costes, dudas de autoconsumo y simulación solar. Se aclara
  que el ejemplo de tres horas requiere ampliar el motor actual; las nuevas
  capacidades quedan pendientes y no cambian el alcance de la primera publicación.
- **19-11-2026:** Se documenta el objetivo de ayudar a hogares a entender su
  consumo. Tras publicar el planificador de dos horas, la siguiente prioridad
  pasa a ser el análisis de consumos reales y escenarios, seguido del chat sobre
  esos servicios y el autoconsumo. Se actualizan README, decisiones y esta lista;
  formatos, tarifas admitidas y tratamiento de archivos quedan por definir.
- **20-11-2026:** Al retomar el proyecto se comprueban `origin` en GitHub y
  `main` siguiendo `origin/main` en `a0eef81`. README, TASKS y decisiones tienen
  cambios pendientes de commit. El siguiente paso guiado es guardar esa
  documentación y crear `development`, antes de preparar `feature/ci`.
- **20-11-2026:** Durante la revisión Aitor guarda la definición del producto
  en `e3ca322`. Quedan por guardar las actualizaciones de progreso en README
  y TASKS, subir `main` y crear `development` con seguimiento remoto.
- **20-11-2026:** Se comprueba `development` creada localmente en `e3ca322`,
  todavía sin seguimiento remoto. Quedan README y TASKS modificados y `main`
  un commit por delante de `origin/main`. Se prepara el paso guiado para guardar
  el progreso, actualizar y subir ambas ramas, y crear `feature/ci`.
- **20-11-2026:** Aitor decide trabajar directamente en `development` durante
  la preparación de la primera publicación. CI se configurará en esa rama;
  las ramas por tarea y pull requests quedan para después del despliegue inicial.
  El siguiente paso es guardar la documentación pendiente, subir `development`
  y promover ese avance a `main`.
