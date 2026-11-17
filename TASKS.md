# Tareas — Asistente energético

Actualizado: 17-11-2026.

Proyecto personal de portfolio: motor Python y web pública con Django.
Trabajamos al ritmo de Aitor, una tarea cada vez, explicando qué hacemos y por qué.
Aitor ejecuta los pasos y escribe el código con ayuda. El asistente solo modifica
archivos cuando Aitor lo pide expresamente, como esta lista.

Marcar `[x]` únicamente cuando el resultado esté comprobado. Mantener pendientes
las tareas que solo estén propuestas. Actualizar esta lista conforme avancemos.

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
- [ ] Normalizar y validar la zona Europe/Madrid antes de admitir fechas arbitrarias.
- [ ] Definir soporte o rechazo explícito de días con cambio de hora y horarios que crucen medianoche.
- [ ] Tratar respuestas vacías o malformadas y precios no finitos antes de calcular. **Siguiente paso guiado: validar los precios recibidos.**
- [ ] Definir cómo detectar datos caducados y qué mostrar si faltan precios o falla la API.

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
- [ ] Decidir cómo almacenar y actualizar los precios según la necesidad real.
- [x] Probar el recorrido completo con precios simulados: formulario → cálculo → resultado.
- [x] Probar mensajes, conservación de campos y ausencia de recomendación ante fallos HTTP, ValueError y precios vacíos o incompletos.
- [x] Comprobar que una búsqueda correcta después de un fallo muestra el resultado y elimina el error.
- [x] Ejecutar las 24 pruebas sin red: siete del recorrido web y 17 de servicios.
- [ ] Mejorar la presentación del formulario y del resultado para su uso público.
- [ ] Configurar comprobaciones automáticas en GitHub Actions al preparar el remoto.
- [ ] Preparar la configuración de producción: secretos, DEBUG, hosts y HTTPS.
- [ ] Elegir alojamiento, revisar costes y decidir el despliegue con Aitor.
- [ ] Publicar y comprobar que el planificador funciona desde fuera del equipo.
- [ ] Añadir enlace, captura, instrucciones y decisiones al portfolio.

## 5. Añadir el chat después del planificador público

- [ ] Definir qué aporta el chat y qué preguntas atenderá.
- [ ] Elegir la integración y revisar costes y gestión de claves.
- [ ] Conectar el chat al motor: los cálculos y precios proceden de herramientas verificadas.
- [ ] Definir respuestas ante datos ausentes y peticiones fuera de alcance.
- [ ] Evaluar respuestas y añadir controles de uso antes de publicarlo.

## Más adelante

- [ ] Valorar skills propias si aparecen procedimientos que repetimos a menudo.
- [ ] Reconsiderar otras funciones energéticas después de completar el primer alcance.
- [ ] Retomar el asistente del paro únicamente cuando se decida expresamente.

## Tareas necesarias añadidas y qué resuelven

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
- **Zona horaria, respuestas malformadas y precios no finitos:** pendientes antes de
  admitir consultas generales; evitan cálculos con fechas mal interpretadas o datos inválidos.
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
