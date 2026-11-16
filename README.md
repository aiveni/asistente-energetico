# Planificador energético

Proyecto personal de portfolio construido con Python.
La futura web utilizará Django.

## Qué hace actualmente

Busca las dos horas consecutivas más baratas dentro de un horario
indicado, usando precios ficticios.

El cálculo supone una potencia constante de 1 kW. El coste mostrado
corresponde únicamente a la energía consumida durante esas dos horas.

## Preparación

Requisitos: Python 3.12 o superior y uv instalado fuera del entorno virtual.

```powershell
uv sync
```

## Ejecutar el ejemplo

```powershell
uv run python motor.py
```

Para el horario 18:00–22:00, el ejemplo devuelve 19:00–21:00
con un coste de 0,20 €.

## Ejecutar las pruebas

```powershell
uv run python -m unittest -v
```

## Límites actuales

- Solo admite horas enteras de un mismo día.
- Necesita precios para todas las horas del horario solicitado.
- En caso de empate, elige la primera franja.
- No consulta precios reales ni calcula una factura completa.

## Próximos pasos

1. Incorporar datos reales y verificar sus unidades e intervalos.
2. Construir y publicar el planificador con Django.
3. Añadir un chat que utilice el motor.