# Tareas — Asistente energético

Actualizado: 17-11-2026.

Proyecto personal de portfolio: motor Python y web pública con Django.
Trabajamos al ritmo de Aitor, una tarea cada vez, explicando qué hacemos y por qué.
Aitor ejecuta los pasos y escribe el código con ayuda. El asistente solo modifica
archivos cuando Aitor lo pide expresamente, como esta lista.
Crear commits únicamente cuando Aitor lo autorice expresamente.

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
- [ ] Elegir un backend de caché compartido al preparar el despliegue con varios procesos.
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
- [ ] Conectar un repositorio remoto de GitHub y realizar el primer push. **Siguiente paso guiado.**
- [ ] Configurar comprobaciones automáticas en GitHub Actions después de conectar el remoto.
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
- [ ] Dar soporte completo a días de 23 o 25 horas con intervalos y duración real, si se amplía el alcance.
- [ ] Retomar el asistente del paro únicamente cuando se decida expresamente.

## Tareas necesarias añadidas y qué resuelven

- **Repositorio remoto:** permite conservar una copia en GitHub y ejecutar las
  comprobaciones automáticas allí. El repositorio local todavía no tiene remoto.
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
