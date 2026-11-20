# Asistente energético

Asistente para ayudar a hogares a entender su consumo eléctrico y comparar
decisiones sobre cuándo consumir, con datos, cálculos y supuestos explícitos.
Proyecto personal de portfolio con motor Python y web Django en desarrollo local.
El aprendizaje de datos de energía e IA aplicada forma parte del objetivo.

## Objetivo y entregas previstas

El planificador es la primera entrega. La siguiente ampliación prioritaria será
analizar consumos reales aportados por el usuario. Después, el chat podrá utilizar
esos resultados para responder preguntas y comparar escenarios; el autoconsumo
se incorporará sobre esa base. La simulación de producción solar queda para una
fase posterior que todavía requiere concretar sus datos y alcance.

| Entrega | Utilidad prevista | Situación |
| --- | --- | --- |
| Planificador público | Elegir las dos horas consecutivas más baratas dentro del horario disponible. | Funciona en local; publicación pendiente. |
| Análisis de consumos | Subir un archivo admitido, indicar una tarifa y revisar consumos y costes por intervalos. | Próxima ampliación tras publicar; formato y tarifas admitidas por definir. |
| Chat sobre los datos | Preguntar por los resultados y solicitar comparaciones mediante herramientas Python. | Pendiente, después de validar los cálculos que utilizará. |
| Autoconsumo | Resolver dudas con fuentes oficiales y estudiar consumo y producción cuando haya datos compatibles. | Ampliación posterior. |
| Simulación solar | Estimar producción y comparar escenarios de instalación y consumo. | Idea por concretar. |

El recorrido futuro será: aportar consumos → validar los datos y la tarifa →
mostrar el análisis → definir un cambio posible → comparar escenarios → explicar
el resultado. Los consumos que se puedan desplazar y sus límites deberán
confirmarse con el usuario. Cada comparación conservará la misma energía y
explicará qué precios y conceptos de coste utiliza.

## Alcance de la primera entrega

La primera publicación ofrecerá un formulario de fecha y horario dentro de un
mismo día, precios PVPC peninsulares, recomendación de dos horas consecutivas,
tabla para comprobarla y mensajes cuando falten datos o la entrada no sea válida.
El coste de referencia corresponde a 1 kW constante durante las dos horas.
La interfaz se adapta a móvil y explica las limitaciones de horario y cálculo.

La entrega se considerará terminada cuando las comprobaciones automáticas sean
correctas y la búsqueda pueda utilizarse desde una URL pública con configuración
de producción y HTTPS. La subida de consumos, las duraciones configurables, la
comparación de aparatos y el chat pertenecen a entregas posteriores.

## Qué hace actualmente

La página recibe fecha y horas mediante un formulario GET, valida la búsqueda,
obtiene precios desde la caché o REData y muestra la franja recomendada. También incluye un ejemplo
ficticio que se puede comprobar a mano y pruebas que funcionan sin internet.

El cálculo supone una potencia constante de 1 kW. El coste mostrado
corresponde únicamente a la energía consumida durante esas dos horas, sin
representar una factura completa. La web todavía no está publicada.

La pantalla incluye selectores de horas, una tarjeta con la recomendación y una
tabla de precios del horario consultado que destaca los dos intervalos elegidos.
Los estados inicial y de error conservan una explicación sin inventar precios.
La interfaz está en español y se adapta a escritorio y móvil.

Motivos de la estructura y del cálculo:
[docs/decisiones.md](docs/decisiones.md).

## Preparación

Requisitos: Python 3.12 o superior y uv instalado fuera del entorno virtual.
El entorno actual utiliza Python 3.15.2 y Django 6.1.3. Las dependencias se
declaran en `pyproject.toml` y sus versiones resueltas se guardan en `uv.lock`.
`tzdata` se declara como dependencia directa para disponer de los datos de zona
horaria también en Windows.
`python-dotenv` permite cargar la configuración local desde `.env`.

Desde la raíz del repositorio:

```powershell
uv sync
```

Para la primera instalación, crea `.env` en la raíz a partir de `.env.example`.
Si ya tienes un `.env`, conserva sus valores. Para desarrollo local configura
`DJANGO_DEBUG=true`, `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1` y una
`DJANGO_SECRET_KEY` propia. Puedes generar la clave en tu terminal con:

```powershell
uv run python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Guarda el resultado como valor de `DJANGO_SECRET_KEY` en `.env`. Mantén esa clave
entre arranques. `.env` está excluido de Git; `.env.example` es la plantilla
versionada y deja la clave vacía.

La configuración carga `.env` antes de leer las variables, sin sobrescribir las
que ya estén definidas en el entorno. El valor `true` activa DEBUG; por defecto
queda desactivado. El arranque comunica un error si falta la clave o, con DEBUG
desactivado, si faltan los hosts permitidos. Estos se escriben separados por
comas, con nombres de host sin esquema ni puerto.

## Arrancar la web en local

```powershell
uv run python manage.py migrate
uv run python manage.py runserver
```

`migrate` crea las tablas de las aplicaciones que Django incluye por defecto
en la base SQLite local. Todavía no hay modelos propios de consumo o precios.
`db.sqlite3` está excluido de Git.

Abre http://127.0.0.1:8000/ y elige una fecha y un horario dentro del mismo día.
Para detener el servidor, pulsa Ctrl+C. Las descargas y actualizaciones necesitan
internet; una copia vigente permite reutilizar los precios. Las pruebas automáticas
utilizan respuestas simuladas.

## Ejecutar los ejemplos desde la terminal

Ejemplo ficticio, sin conexión:

```powershell
uv run python -m energia.servicios.motor
```

Para el horario 18:00–22:00, el ejemplo devuelve 19:00–21:00
con un coste de 0,20 €.

Ejemplo con consulta real para el 15-11-2026:

```powershell
uv run python -m energia.servicios.consultar_precios
```

La muestra revisada para 18:00–22:00 da 20:00–22:00 y 0,44651 € a 1 kW.
Este comando consulta REData directamente; la caché se incorpora en la capa web.
Los ejemplos se ejecutan como módulos (`-m`) porque ahora pertenecen al paquete
`energia.servicios` y utilizan sus imports internos.

## Ejecutar las pruebas

```powershell
uv run python manage.py test -v 2
```

Actualmente hay 64 pruebas: seis del motor, veintidós del adaptador, once de la
consulta HTTP simulada, dieciséis del recorrido web, seis de caché y tres del
formulario. Las pruebas web no usan una
base de datos. El comando prepara la configuración de Django para ejecutarlas.

GitHub Actions ejecuta la instalación desde `uv.lock` y las pruebas al subir
cambios a `development` y `main`, y en pull requests hacia esas ramas. El workflow
está en `.github/workflows/ci.yml` y define las variables necesarias para las
pruebas. La clave de CI debe ser ficticia y distinta de las claves de los entornos
local y de producción.

Se comprueba que los fallos de conexión, timeout, estado HTTP y los datos no
utilizables muestran un error sin recomendación, conservan los campos y permiten
repetir la búsqueda. También se prueban cuerpos vacíos, HTML, JSON truncado,
campos ausentes, tipos inesperados y registros sin una fecha y hora válida.
Las pruebas de zona horaria cubren invierno, verano, UTC, cambios de fecha al
convertir, ausencia de desplazamiento y rechazo de días con cambio de hora.
Las pruebas de caché verifican reutilización por fecha, caducidad con un reloj
simulado y reintentos tras errores o datos incompletos. Cada prueba usa una caché
aislada para evitar resultados que dependan de pruebas anteriores.
La tabla se comprueba con precios de fuera del horario, precios negativos y el
límite de las 24:00. Los selectores entregan enteros al motor y rechazan opciones
fuera de rango y horarios inválidos.

## Estructura

```text
config/                        Configuración y rutas generales de Django
energia/
    forms.py                   Campos y validaciones del formulario
    views.py                   Coordinación entre formulario, servicios y plantilla
    cache_precios.py            Reutilización temporal de precios mediante Django
    urls.py                    Rutas de la aplicación
    servicios/
        motor.py               Cálculo independiente de Django y de la red
        adaptador_precios.py   Validación y conversión de registros PVPC
        consultar_precios.py   Consulta HTTP a REData
    tests/                     Pruebas del motor, adaptador, consulta y web
    templates/energia/         Plantillas de esta aplicación
    static/energia/            CSS de la interfaz, sin fuentes ni librerías externas
docs/                          Decisiones y contexto técnico
manage.py                      Entrada para los comandos de Django
pyproject.toml                 Metadatos y dependencias del proyecto
uv.lock                        Versiones resueltas
```

Los servicios se pueden importar sin iniciar peticiones HTTP ni cargar Django.
Las vistas los utilizan y presentan el resultado. Los motivos de esta separación
están en [docs/decisiones.md](docs/decisiones.md).

## Interfaz y comprobación local

`energia/templates/energia/inicio.html` presenta formulario, resultado y tabla.
`energia/static/energia/estilos.css` contiene los estilos; Django lo sirve con
runserver durante el desarrollo. Los selectores muestran horas como 18:00 y el
formulario ofrece inicialmente la fecha local de hoy, sin consultar precios hasta
que se envía la búsqueda.

La vista prepara la tabla después de calcular correctamente. Solo incluye el
horario solicitado y marca los dos intervalos recomendados. Los importes se
muestran con cinco decimales y formato español; el cálculo mantiene los Decimal
originales. Ante errores no se muestra la tabla ni una recomendación anterior.

Se han revisado capturas de páginas renderizadas por Django con datos de prueba:
estados inicial, resultado y error en escritorio, y resultado y error en móvil,
incluidos anchos de 320 y 390 píxeles sin desbordamiento horizontal de la página.
Las búsquedas se verifican automáticamente con el cliente de pruebas de Django.
La preparación de los archivos estáticos para producción sigue pendiente.

## Caché de precios de la web

`energia/cache_precios.py` guarda días completos con las 24 horas ya validadas.
La clave identifica PVPC, sistema peninsular, zona, formato y fecha. Cambiar el
horario reutiliza esos precios y ejecuta de nuevo el cálculo de la franja.

La política inicial es de cinco minutos desde la descarga, configurables mediante
`PRECIOS_CACHE_TIMEOUT` en `config/settings.py`. Leer la copia no renueva el plazo.
Al caducar se vuelve a consultar REData; si falla, la web muestra el error sin
servir la copia vencida. Los errores y precios incompletos no se guardan. Una
muestra parcial puede resolver un horario completo, pero la siguiente petición
volverá a consultar la fuente.

Se usa la [caché en memoria de Django](https://docs.djangoproject.com/en/6.1/topics/cache/#local-memory-caching)
para desarrollo: es por proceso y se pierde al reiniciar. El backend compartido
para producción queda pendiente. Esta caché evita descargas repetidas; su plazo
no certifica la fecha de última publicación de los datos en la fuente.

## Fuente de datos

- [Documentación de REData de Red Eléctrica](https://www.ree.es/es/datos/apidatos).
- Serie PVPC con identificador 1001, sistema peninsular 8741.
- El adaptador convierte de €/MWh a €/kWh dividiendo entre 1.000.
- La fecha solicitada y las horas del formulario se interpretan en Europe/Madrid.
  Los registros deben indicar su desplazamiento UTC y se convierten a esta zona
  antes de comprobar día, hora y duplicados.

## Límites actuales

- Solo admite horas enteras de un mismo día.
- Necesita precios para todas las horas del horario solicitado.
- En caso de empate, elige la primera franja.
- Rechaza registros de otro día, fuera del inicio de una hora o con horas repetidas.
- Rechaza precios ausentes, texto, booleanos, NaN e infinitos; conserva cero y negativos.
- Valida los campos utilizados de la respuesta JSON y exige una lista no vacía
  de registros con fecha y hora ISO de texto y separador T.
- No cruza medianoche. Rechaza todos los días con cambio de hora en esta versión,
  incluso si el horario solicitado queda fuera del salto, porque el motor representa
  días normales de 24 horas. La web informa de esta limitación.
- Queda pendiente revisar la antigüedad de la publicación de la fuente, distinta
  de la caducidad de cinco minutos de nuestra copia.
- La caché es local al proceso; el backend para producción se decidirá al desplegar.
- Los ajustes de Django son de desarrollo local; la preparación de producción
  sigue pendiente.

## Próximos pasos

1. Completar la comprobación de CI en `main` al promover el siguiente avance estable desde `development`. El [flujo de ramas](docs/decisiones.md#flujo-de-ramas-durante-el-arranque) queda documentado.
2. Revisar los ajustes de producción y publicar el planificador de dos horas.
3. Definir y validar la primera entrega de análisis de consumos reales y comparación de escenarios.
4. Conectar el chat a los servicios comprobados y ampliar después hacia autoconsumo.
