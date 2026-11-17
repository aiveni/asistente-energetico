"""Convierte y valida registros PVPC para el motor, sin consultar internet."""

from datetime import date, datetime
from decimal import Decimal


def convertir_precios(registros, fecha_esperada):
    """Convierte registros PVPC de €/MWh a un diccionario de horas y €/kWh.

    Pensado para la muestra horaria de un solo día que hemos revisado.
    Rechaza registros fuera del inicio de una hora y horas repetidas para
    evitar interpretar intervalos parciales o sobrescribir precios.

    fecha_esperada es el día solicitado en formato YYYY-MM-DD. Cada registro
    debe pertenecer a ese día según la fecha local que trae la respuesta.

    Los precios deben ser int, float o Decimal finitos. Se admiten cero y
    negativos; se rechazan valores ausentes, texto y booleanos con ValueError.

    registros debe ser una lista no vacía de objetos con datetime como texto
    ISO con separador T. Los formatos inesperados también producen ValueError.
    """
    dia_esperado = date.fromisoformat(fecha_esperada)
    if not isinstance(registros, list) or not registros:
        raise ValueError("Los registros PVPC deben ser una lista no vacía.")

    precios = {}

    for registro in registros:
        if not isinstance(registro, dict):
            raise ValueError("Cada registro PVPC debe ser un objeto JSON.")

        fecha_texto = registro.get("datetime")
        if not isinstance(fecha_texto, str) or "T" not in fecha_texto:
            raise ValueError("Cada registro debe contener una fecha y hora ISO con separador T.")

        try:
            fecha_hora = datetime.fromisoformat(fecha_texto)
        except ValueError as error:
            raise ValueError("El registro no contiene una fecha y hora ISO válida.") from error

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

        valor = registro.get("value")
        # bool hereda de int en Python, pero true y false no son precios.
        if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
            raise ValueError("Cada registro debe contener un precio numérico.")

        # 1 MWh equivale a 1.000 kWh; el motor necesita precios en €/kWh.
        # Pasamos por texto para no convertir el float directamente a Decimal.
        precio_mwh = Decimal(str(valor))
        if not precio_mwh.is_finite():
            raise ValueError("Los precios deben ser números finitos.")

        precios[hora] = precio_mwh / Decimal("1000")

    return precios
