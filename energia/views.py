"""Coordina el formulario, la consulta de precios y el resultado de la web."""

import httpx
from django.shortcuts import render

from .cache_precios import obtener_precios_con_cache
from .forms import FranjaForm
from .servicios.motor import buscar_mejor_franja


def inicio(request):
    """Muestra el formulario GET y calcula si fecha y horario son válidos.

    Reutiliza los precios mediante la caché y calcula cada horario por separado.
    Entrega el resultado y los precios del horario a la plantilla. Los errores
    HTTP y de datos se muestran en el formulario, conservando los valores
    introducidos y sin mostrar precios de una búsqueda que no se pudo calcular.
    """
    formulario = FranjaForm(request.GET or None)
    resultado = None
    detalle_precios = []

    if formulario.is_valid():
        datos = formulario.cleaned_data
        fecha = datos["fecha"]

        try:
            precios = obtener_precios_con_cache(fecha.isoformat())
            hora, coste = buscar_mejor_franja(
                precios,
                inicio=datos["inicio"],
                fin=datos["fin"],
            )
        except httpx.HTTPError:
            formulario.add_error(
                None,
                "No hemos podido consultar los precios. Inténtalo de nuevo.",
            )
        except ValueError:
            formulario.add_error(
                None,
                "No hay datos horarios utilizables para esa fecha y horario.",
            )
        else:
            resultado = {
                "fecha": fecha,
                "inicio": hora,
                "fin": hora + 2,
                "coste": coste,
                "disponible_desde": datos["inicio"],
                "disponible_hasta": datos["fin"],
            }
            # La tabla muestra solo el horario pedido y destaca las dos horas elegidas.
            detalle_precios = [
                {
                    "inicio": intervalo,
                    "fin": intervalo + 1,
                    "precio": precios[intervalo],
                    "seleccionada": hora <= intervalo < hora + 2,
                }
                for intervalo in range(datos["inicio"], datos["fin"])
            ]

    return render(
        request,
        "energia/inicio.html",
        {
            "formulario": formulario,
            "resultado": resultado,
            "detalle_precios": detalle_precios,
        },
    )
