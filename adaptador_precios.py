"""Conversión de registros PVPC al formato del motor."""

from datetime import date, datetime
from decimal import Decimal


def convertir_precios(registros, fecha_esperada):
    """Convierte registros PVPC de €/MWh a un diccionario de horas y €/kWh.

    Pensado para la muestra horaria de un solo día que hemos revisado.
    Rechaza registros fuera del inicio de una hora y horas repetidas para
    evitar interpretar intervalos parciales o sobrescribir precios.

    fecha_esperada es el día solicitado en formato YYYY-MM-DD. Cada registro
    debe pertenecer a ese día según la fecha local que trae la respuesta.
    """
    dia_esperado = date.fromisoformat(fecha_esperada)
    precios = {}

    for registro in registros:
        fecha_hora = datetime.fromisoformat(registro["datetime"])

        # Comprobamos el día antes de quedarnos solo con la hora.
        if fecha_hora.date() != dia_esperado:
            raise ValueError("Los precios no pertenecen al día solicitado.")

        if (
            fecha_hora.minute != 0
            or fecha_hora.second != 0
            or fecha_hora.microsecond != 0
        ):
            raise ValueError(
                "El motor solo admite registros al inicio de cada hora."
            )

        hora = fecha_hora.hour

        if hora in precios:
            raise ValueError("El motor actual no admite horas repetidas.")

        # 1 MWh equivale a 1.000 kWh; el motor necesita precios en €/kWh.
        # Pasamos por texto para no convertir el float directamente a Decimal.
        precio_mwh = Decimal(str(registro["value"]))
        precios[hora] = precio_mwh / Decimal("1000")

    return precios
