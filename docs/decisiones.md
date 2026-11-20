# Decisiones del proyecto

Actualizado: 19-11-2026. Contexto para retomar el trabajo y revisar sus motivos.

## Producto y ritmo

El objetivo es un asistente energético público para ayudar a hogares a entender
su consumo y comparar decisiones sobre él, con datos y supuestos comprobables.
El proyecto sirve también como portfolio y aprendizaje de datos de energía e IA.

El recorrido inicial fue entorno Windows con Git y uv, motor ficticio, datos
reales y planificador web. El 19-11-2026 se concreta la siguiente prioridad:
publicar el planificador, incorporar análisis de consumos reales, conectar el
chat a los servicios validados y ampliar después hacia autoconsumo. La simulación
solar queda como idea posterior. El asistente del paro sigue aplazado.

Aitor avanza por pasos y comprende el motivo de cada decisión; los cambios del
asistente se hacen cuando se solicitan. Los commits solo se crean con autorización
expresa de Aitor.

## Alcance de producto y criterio de entrega

La primera publicación mantiene el motor actual de dos horas consecutivas dentro
de un mismo día, con precios PVPC peninsulares y referencia de consumo constante
de 1 kW. Incluye formulario, resultado verificable, tabla, mensajes de error y una
interfaz para escritorio y móvil. Termina al comprobar pruebas, configuración de
producción y acceso desde una URL pública con HTTPS. El alcance se resume también
en README y el trabajo pendiente se mantiene en TASKS.

La siguiente entrega prioriza el análisis de archivos de consumo: revisar cuándo
se consume, calcular costes para una tarifa admitida y comparar cambios definidos
por el usuario. El primer formato de archivo y el primer tipo de tarifa se
elegirán antes de implementar la subida. Se comprobará primero con datos
sintéticos y ejemplos manuales, después con una muestra real anonimizada.

Una curva agregada no identifica por sí sola qué aparatos se pueden desplazar.
Las simulaciones pedirán energía desplazable, disponibilidad y restricciones al
usuario, conservarán el consumo total y mostrarán las hipótesis. Los costes
deberán corresponder a los precios, fechas e intervalos de esa tarifa; la cobertura
de conceptos de factura se documentará en cada versión.

La incorporación de archivos requiere definir validación de formato, unidades,
zona horaria, intervalos repetidos o ausentes y tratamiento de los datos del hogar.
Se decidirá la retención mínima y se limitarán los datos enviados al modelo a lo
necesario para responder. Las muestras y registros de prueba usarán datos
sintéticos o anonimizados.

Los cálculos y escenarios serán servicios Python independientes y comprobables.
El chat podrá solicitarlos mediante function calling y explicar sus resultados.
RAG se evaluará para preguntas documentales sobre autoconsumo con fuentes
oficiales. LangChain y LangGraph siguen siendo opciones de aprendizaje y
evaluación, con una decisión de adopción pendiente.

Antes de ampliar cada entrega se preparará una comprobación con usuarios para
ver si entienden el resultado, los supuestos y qué decisión les permite tomar.

## Motor determinista separado de la web

`energia/servicios/motor.py` solo calcula. Recibe precios como Decimal en €/kWh
y un horario [inicio, fin) con horas enteras de un mismo día. Devuelve la hora
de inicio y el coste mínimo de dos horas consecutivas. En empate conserva la
primera franja porque solo sustituye el mínimo ante un coste estrictamente menor.

La suma de precios representa euros para un aparato de 1 kW constante durante
dos horas: consume 1 kWh en cada hora. No representa el precio medio, el consumo
variable de cualquier aparato ni una factura completa.

La función no necesita Django ni internet. Esto permite comprobarla con números
pequeños y reutilizarla desde la web y, después, desde un chat.

## Consulta y adaptación separadas

`consultar_precios.py` solicita el PVPC peninsular a REData y selecciona la serie
por su ID 1001. `adaptador_precios.py` comprueba fechas, rechaza registros fuera
del inicio de una hora y evita sobrescribir horas repetidas. Convierte €/MWh
a €/kWh mediante Decimal y división entre 1.000.

El adaptador exige precios numéricos finitos: int, float o Decimal. Rechaza el
campo ausente, null, texto, booleanos, NaN e infinitos con ValueError para que
la vista pueda mostrar su mensaje de datos no utilizables. Los booleanos se
comprueban expresamente porque bool hereda de int en Python. Cero y los precios
negativos siguen siendo válidos; esta comprobación se hace antes de operar.

La conversión se puede probar sin acceder a la API. Los errores HTTP y de espera
se propagan hasta quien llama; la vista los convierte en mensajes del formulario.
La consulta comprueba que la raíz JSON sea un objeto, included una lista y cada
serie tenga un ID de texto o entero. Para el PVPC exige un objeto attributes.
El adaptador exige que values sea una lista no vacía de objetos con datetime
como texto ISO con separador T, incluyendo una hora interpretable. Los metadatos
que no se utilizan no son obligatorios.

Estas comprobaciones se hacen antes de acceder a cada campo. Así se comunica
ValueError ante datos inesperados sin capturar indiscriminadamente otros errores
del programa. Los cuerpos vacíos, HTML y JSON truncado ya producen ValueError al
decodificar la respuesta. La vista conserva la búsqueda y muestra el error de datos.

## Normalización de zona horaria

La fecha pedida y las horas del formulario son locales de Europe/Madrid. El
adaptador exige un desplazamiento UTC explícito en cada registro, interpreta el
instante con datetime.fromisoformat y lo convierte con astimezone y ZoneInfo.
Después comprueba fecha, hora exacta y duplicados. Nunca presupone la zona del
equipo para una marca temporal sin desplazamiento.

Esto permite aceptar, por ejemplo, las 23:00 UTC del día anterior como las 00:00
del día pedido en invierno. Los desplazamientos de verano e invierno proceden
de la base IANA, sin fijar manualmente UTC+1 o UTC+2. Django usa la misma zona
en TIME_ZONE y conserva USE_TZ=True.

Se declara tzdata como dependencia directa para que los servicios funcionen
también en Windows, donde no siempre hay una base IANA del sistema disponible.
Véase la [documentación de zoneinfo](https://docs.python.org/3/library/zoneinfo.html).

La primera versión rechaza los días con cambio de hora, detectando la diferencia
de desplazamiento entre el principio y el final del día local. El motor actual
representa horas enteras 0–23; aceptar días de 23 o 25 horas podría dar resultados
con una hora inexistente o perder una hora repetida. Dar soporte completo a esos
días requiere representar intervalos con instantes y duración real, y queda para
un paso posterior. La limitación aparece en la página y se prueba desde la web.

## Organización dentro de la app energia

El código que antes estaba en la raíz se agrupa en `energia/servicios/`, y las
pruebas en `energia/tests/`. Hay una sola aplicación de dominio por ahora; las
subcarpetas permiten encontrar cada pieza sin introducir otra herramienta.

`forms.py` valida la entrada de la web; `views.py` coordina los servicios;
`templates/energia/` presenta la respuesta. `config/` conserva la configuración
general de Django. Los paquetes de servicios no importan Django.

`energia/cache_precios.py` integra la caché de Django por encima de la consulta.
Así la descarga, la adaptación y el cálculo siguen siendo reutilizables sin
configuración web. La vista llama a obtener_precios_con_cache y luego al motor.

Los imports y las rutas de patch en las pruebas cambian con los módulos movidos.
Los ejemplos se ejecutan desde la raíz mediante `python -m energia.servicios.motor`
y `python -m energia.servicios.consultar_precios`.

## Formulario GET

La búsqueda consulta información sin modificar registros de negocio. GET conserva
fecha y horario en la URL para repetir o compartir la búsqueda. Primero se valida
el formulario; una petición vacía o inválida no debe consultar precios.

## Caché diaria y caducidad

La web reutiliza precios de un día completo durante 300 segundos desde su
descarga. Es una política inicial de desarrollo, configurable con
PRECIOS_CACHE_TIMEOUT, sin renovar el plazo en cada lectura. La clave identifica
el indicador 1001, sistema 8741, Europe/Madrid, versión del formato y fecha.
El resultado de la recomendación se calcula para cada horario.

Se guarda únicamente un diccionario con las 24 horas, después de la validación
del servicio. Una respuesta parcial se entrega al motor para que compruebe el
horario solicitado, pero no se guarda; esto permite volver a consultar si la
fuente completa los datos. Las excepciones tampoco se guardan. Si una copia
caduca y falla la actualización, se muestra el error en lugar de servir esa copia.

LocMemCache permite practicar este comportamiento sin instalar otro servicio.
La copia es temporal y por proceso; antes de publicar con varios procesos habrá
que decidir un backend compartido. La caducidad de la copia no equivale a validar
la fecha de última publicación de REData. Referencia:
[caché de Django](https://docs.djangoproject.com/en/6.1/topics/cache/).

## Presentación de la búsqueda

La interfaz utiliza plantillas de Django y CSS dentro de la aplicación, con
tipografías locales y SVG decorativos sencillos. Esto mantiene el arranque con
las herramientas Python existentes. Los estilos se descubren mediante staticfiles
en `energia/static/energia/`, con el mismo criterio de nombres que las plantillas.

Las horas se muestran como opciones legibles con TypedChoiceField y coerce=int.
El motor sigue recibiendo enteros; el formulario valida la pertenencia a las
opciones y la relación entre inicio y fin. La fecha inicial usa timezone.localdate
para seguir Europe/Madrid. LANGUAGE_CODE se cambia a es para presentar importes
y errores con formato español. Referencia:
[campos de formulario](https://docs.djangoproject.com/en/6.1/ref/forms/fields/#typedchoicefield).

La vista prepara detalle_precios después de un cálculo correcto: un registro
por intervalo del horario solicitado, con precio e indicador de selección.
La plantilla destaca los dos intervalos elegidos y muestra la referencia de
1 kW constante durante dos horas. El formato visual de cinco decimales no
modifica los Decimal con los que se calcula. Ante errores la lista queda vacía.

Los controles tienen etiquetas, ayudas y mensajes asociados; hay foco visible,
enlace para saltar al formulario y una tabla con encabezados y selección textual.
La adaptación móvil se ha revisado en el navegador con capturas de HTML generado
por Django y datos de prueba. Las capturas y perfiles temporales están en
`_local/ui_preview/`, excluido de Git. Las pruebas funcionales utilizan el cliente
de Django y las consultas simuladas, sin depender de la API en la revisión visual.

## Dependencias y comprobaciones

uv gestiona `pyproject.toml` y `uv.lock`. La instalación actual usa Python 3.15.2
y Django 6.1.3. `.venv`, la base SQLite local y los documentos de `_local/` se
excluyen de Git. Las tablas incluidas por Django no implican tener modelos
propios ni almacenamiento de los precios consultados.

Las pruebas se ejecutan con `python manage.py test`. Son 64: motor (6), adaptador
(22), consulta HTTP (11), web (16), caché (6) y formulario (3). Las llamadas externas se simulan para comprobar
éxitos y errores sin depender de la disponibilidad de REData. Las pruebas de
la web utilizan SimpleTestCase porque este recorrido no accede a una base de datos.

Las pruebas web incluyen fallos de conexión, timeout, estado HTTP 503 y errores
de validación del servicio. También comprueban precios vacíos o incompletos con
el motor real, la conservación de los campos y una búsqueda correcta después
de un fallo. Una prueba adicional recorre la consulta y el adaptador reales con
una respuesta HTTP simulada que contiene precios inválidos, incluido 1e999,
que el lector JSON convierte en infinito. La web muestra el error sin producir
una recomendación. También se comprueba el recorrido con cuerpos vacíos, HTML,
estructuras JSON inesperadas y registros sin fecha de texto, sin mostrar un error 500.
Las pruebas de normalización verifican los resultados de invierno y verano, el
cambio de fecha entre UTC y Madrid, los duplicados tras convertir y el rechazo
de registros sin zona y días con cambio de hora. La muestra real mantiene 20–22
y 0,44651 euros aunque sus marcas se expresen en UTC.

Las pruebas de caché utilizan un backend en memoria aislado y simulan el reloj,
sin dormir. Comprueban que leer no prolongue la caducidad y que no se guarden
errores ni datos parciales. Un recorrido web prueba dos horarios distintos con
una sola descarga, y otro recupera un día completo después de una respuesta parcial.
Las pruebas de presentación comprueban que la tabla solo incluye el horario
pedido y destaca dos intervalos, incluyendo precios negativos y el límite de
medianoche. Los campos horarios se prueban con límites válidos e inválidos para
conservar el contrato del motor al usar selectores.

## Documentación y skills

Los módulos, clases y funciones tienen docstrings que describen su propósito,
contrato o caso probado. README explica el uso, TASKS registra lo comprobado y
este archivo conserva las decisiones. Una skill propia se valorará cuando exista
un procedimiento repetido que la justifique.
