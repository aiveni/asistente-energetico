"""Consulta el PVPC peninsular y permite ejecutar un ejemplo de planificación.

Importar este módulo no consulta la API. El ejemplo se ejecuta únicamente
al lanzar el archivo directamente.

Desde la raíz: python -m energia.servicios.consultar_precios.
"""

import httpx

from .adaptador_precios import convertir_precios
from .motor import buscar_mejor_franja

URL = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"


def obtener_precios(fecha):
    """Consulta el PVPC peninsular y devuelve precios horarios en €/kWh.

    Recibe la fecha en formato YYYY-MM-DD. Propaga los errores de conexión,
    de estado HTTP y de validación para que quien la llame pueda tratarlos.
    Exige un objeto JSON con una lista included y una serie PVPC identificable;
    los atributos y registros necesarios se validan antes de utilizarlos.
    """
    parametros = {
        "start_date": f"{fecha}T00:00",
        "end_date": f"{fecha}T23:59",
        "time_trunc": "hour",
        "geo_trunc": "electric_system",
        "geo_limit": "peninsular",
        "geo_ids": "8741",
    }

    respuesta = httpx.get(URL, params=parametros, timeout=20)
    # No intentamos calcular si la API devuelve un error HTTP.
    respuesta.raise_for_status()
    datos = respuesta.json()

    if not isinstance(datos, dict):
        raise ValueError("La respuesta de REData debe ser un objeto JSON.")

    series = datos.get("included")
    if not isinstance(series, list):
        raise ValueError("La respuesta de REData debe contener una lista de series.")

    # Identificamos el PVPC por su ID, sin depender del orden de las series.
    for serie in series:
        if not isinstance(serie, dict):
            raise ValueError("Cada serie de REData debe ser un objeto JSON.")

        identificador = serie.get("id")
        if (
            isinstance(identificador, bool)
            or not isinstance(identificador, (str, int))
            or identificador == ""
        ):
            raise ValueError("Cada serie debe contener un identificador válido.")

        if str(identificador) == "1001":
            atributos = serie.get("attributes")
            if not isinstance(atributos, dict):
                raise ValueError("La serie PVPC debe contener un objeto de atributos.")

            # El adaptador comprueba que values sea una lista no vacía de registros.
            registros_pvpc = atributos.get("values")
            break
    else:
        # El else del for se ejecuta si no hemos encontrado la serie con break.
        raise ValueError("La respuesta no contiene la serie PVPC.")

    # El motor recibe {hora_de_inicio: precio_en_euros_por_kWh}.
    return convertir_precios(registros_pvpc, fecha_esperada=fecha)


if __name__ == "__main__":
    # Usamos el día ya revisado para reproducir el ejemplo.
    fecha = "2026-11-15"
    precios_reales = obtener_precios(fecha)

    # Reutilizamos el cálculo probado; la consulta no decide qué franja es mejor.
    hora_elegida, coste_elegido = buscar_mejor_franja(
        precios_reales,
        inicio=18,
        fin=22,
    )

    print(
        f"Fecha: {fecha}. "
        f"Mejor franja: {hora_elegida}:00–{hora_elegida + 2}:00. "
        f"Coste energético a 1 kW: {coste_elegido} euros"
    )
