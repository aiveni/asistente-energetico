# Decisiones del proyecto

Actualizado: 17-11-2026. Contexto para retomar el trabajo y revisar sus motivos.

## Producto y ritmo

El objetivo es un asistente energético público de portfolio. El orden acordado
es entorno Windows con Git y uv, motor ficticio, datos reales, planificador web
y chat. El asistente del paro queda aplazado. Aitor avanza por pasos y comprende
el motivo de cada decisión; los cambios del asistente se hacen cuando se solicitan.

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
La normalización de zona horaria, los cambios de hora y las respuestas malformadas
siguen siendo trabajo pendiente: ordenar el código no añade ese soporte.

## Organización dentro de la app energia

El código que antes estaba en la raíz se agrupa en `energia/servicios/`, y las
pruebas en `energia/tests/`. Hay una sola aplicación de dominio por ahora; las
subcarpetas permiten encontrar cada pieza sin introducir otra herramienta.

`forms.py` valida la entrada de la web; `views.py` coordina los servicios;
`templates/energia/` presenta la respuesta. `config/` conserva la configuración
general de Django. Los paquetes de servicios no importan Django.

Los imports y las rutas de patch en las pruebas cambian con los módulos movidos.
Los ejemplos se ejecutan desde la raíz mediante `python -m energia.servicios.motor`
y `python -m energia.servicios.consultar_precios`.

## Formulario GET

La búsqueda consulta información sin modificar registros de negocio. GET conserva
fecha y horario en la URL para repetir o compartir la búsqueda. Primero se valida
el formulario; una petición vacía o inválida no debe consultar precios.

## Dependencias y comprobaciones

uv gestiona `pyproject.toml` y `uv.lock`. La instalación actual usa Python 3.15.2
y Django 6.1.3. `.venv`, la base SQLite local y los documentos de `_local/` se
excluyen de Git. Las tablas incluidas por Django no implican tener modelos
propios ni almacenamiento de los precios consultados.

Las pruebas se ejecutan con `python manage.py test`. Son 29: motor (6), adaptador
(11), consulta HTTP (4) y web (8). Las llamadas externas se simulan para comprobar
éxitos y errores sin depender de la disponibilidad de REData. Las pruebas de
la web utilizan SimpleTestCase porque este recorrido no accede a una base de datos.

Las pruebas web incluyen fallos de conexión, timeout, estado HTTP 503 y errores
de validación del servicio. También comprueban precios vacíos o incompletos con
el motor real, la conservación de los campos y una búsqueda correcta después
de un fallo. Una prueba adicional recorre la consulta y el adaptador reales con
una respuesta HTTP simulada que contiene precios inválidos, incluido 1e999,
que el lector JSON convierte en infinito. La web muestra el error sin producir
una recomendación. El tratamiento general de estructuras malformadas sigue pendiente.

## Documentación y skills

Los módulos, clases y funciones tienen docstrings que describen su propósito,
contrato o caso probado. README explica el uso, TASKS registra lo comprobado y
este archivo conserva las decisiones. Una skill propia se valorará cuando exista
un procedimiento repetido que la justifique.
