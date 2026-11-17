# Planificador energético

Proyecto personal de portfolio con motor Python y web Django en desarrollo local.
Permite elegir una fecha y un horario para buscar las dos horas consecutivas
más baratas con precios PVPC peninsulares de Red Eléctrica.

## Qué hace actualmente

La página recibe fecha y horas mediante un formulario GET, valida la búsqueda,
consulta REData y muestra la franja recomendada. También incluye un ejemplo
ficticio que se puede comprobar a mano y pruebas que funcionan sin internet.

El cálculo supone una potencia constante de 1 kW. El coste mostrado
corresponde únicamente a la energía consumida durante esas dos horas, sin
representar una factura completa. La web todavía no está publicada.

Progreso: [TASKS.md](TASKS.md). Motivos de la estructura y del cálculo:
[docs/decisiones.md](docs/decisiones.md).

## Preparación

Requisitos: Python 3.12 o superior y uv instalado fuera del entorno virtual.
El entorno actual utiliza Python 3.15.2 y Django 6.1.3. Las dependencias se
declaran en `pyproject.toml` y sus versiones resueltas se guardan en `uv.lock`.

Desde la raíz del repositorio:

```powershell
uv sync
```

## Arrancar la web en local

```powershell
uv run python manage.py migrate
uv run python manage.py runserver
```

`migrate` crea las tablas de las aplicaciones que Django incluye por defecto
en la base SQLite local. Todavía no hay modelos propios de consumo o precios.
`db.sqlite3` está excluido de Git.

Abre http://127.0.0.1:8000/ y elige una fecha y un horario dentro del mismo día.
Para detener el servidor, pulsa Ctrl+C. La consulta real necesita conexión a
internet; las pruebas automáticas utilizan respuestas simuladas.

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
Los ejemplos se ejecutan como módulos (`-m`) porque ahora pertenecen al paquete
`energia.servicios` y utilizan sus imports internos.

## Ejecutar las pruebas

```powershell
uv run python manage.py test -v 2
```

Actualmente hay 24 pruebas: seis del motor, siete del adaptador, cuatro de la
consulta HTTP simulada y siete del recorrido web. Las pruebas web no usan una
base de datos. El comando prepara la configuración de Django para ejecutarlas.

Se comprueba que los fallos de conexión, timeout, estado HTTP y los datos no
utilizables muestran un error sin recomendación, conservan los campos y permiten
repetir la búsqueda. El tratamiento general de respuestas malformadas sigue pendiente.

## Estructura

```text
config/                        Configuración y rutas generales de Django
energia/
    forms.py                   Campos y validaciones del formulario
    views.py                   Coordinación entre formulario, servicios y plantilla
    urls.py                    Rutas de la aplicación
    servicios/
        motor.py               Cálculo independiente de Django y de la red
        adaptador_precios.py   Validación y conversión de registros PVPC
        consultar_precios.py   Consulta HTTP a REData
    tests/                     Pruebas del motor, adaptador, consulta y web
    templates/energia/         Plantillas de esta aplicación
docs/                          Decisiones y contexto técnico
manage.py                      Entrada para los comandos de Django
pyproject.toml                 Metadatos y dependencias del proyecto
uv.lock                        Versiones resueltas
TASKS.md                       Progreso y trabajo pendiente
```

Los servicios se pueden importar sin iniciar peticiones HTTP ni cargar Django.
Las vistas los utilizan y presentan el resultado. Los motivos de esta separación
están en [docs/decisiones.md](docs/decisiones.md).

## Fuente de datos

- [Documentación de REData de Red Eléctrica](https://www.ree.es/es/datos/apidatos).
- Serie PVPC con identificador 1001, sistema peninsular 8741.
- El adaptador convierte de €/MWh a €/kWh dividiendo entre 1.000.

## Límites actuales

- Solo admite horas enteras de un mismo día.
- Necesita precios para todas las horas del horario solicitado.
- En caso de empate, elige la primera franja.
- Rechaza registros de otro día, fuera del inicio de una hora o con horas repetidas.
- No cruza medianoche ni tiene soporte completo de días con cambio de hora.
- La normalización a Europe/Madrid y el tratamiento de respuestas malformadas,
  precios no finitos y datos caducados siguen pendientes.
- Cada búsqueda válida consulta REData; todavía no hay caché de precios.
- Los ajustes de Django son de desarrollo local; la preparación de producción
  se registra como pendiente en TASKS.md.

## Próximos pasos

1. Validar precios no finitos y respuestas malformadas antes del cálculo.
2. Revisar zona horaria, cambios de hora y actualización de precios.
3. Mejorar la presentación, preparar CI y publicar el planificador.
4. Añadir el chat después del planificador público.
