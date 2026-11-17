"""Convierte y valida registros PVPC para el motor, sin consultar internet."""

from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo


ZONA_PENINSULAR = ZoneInfo("Europe/Madrid")


def _normalizar_fecha_hora(fecha_texto):
    """Interpreta un instante ISO con desplazamiento y lo convierte a Madrid.

    Exige zona explícita para no depender de la configuración del equipo.
    astimezone conserva el instante y ajusta fecha, hora y horario de verano.
    """
    if not isinstance(fecha_texto, str) or "T" not in fecha_texto:
        raise ValueError("Cada registro debe contener una fecha y hora ISO con separador T.")

    try:
        fecha_hora = datetime.fromisoformat(fecha_texto)
    except ValueError as error:
        raise ValueError("El registro no contiene una fecha y hora ISO válida.") from error

    if fecha_hora.utcoffset() is None:
        raise ValueError("Cada registro debe indicar su desplazamiento respecto a UTC.")

    return fecha_hora.astimezone(ZONA_PENINSULAR)


def convertir_precios(registros, fecha_esperada):
    """Convierte registros PVPC de €/MWh a un diccionario de horas y €/kWh.

    Pensado para la muestra horaria de un solo día que hemos revisado.
    Rechaza registros fuera del inicio de una hora y horas repetidas para
    evitar interpretar intervalos parciales o sobrescribir precios.

    fecha_esperada es el día solicitado en formato YYYY-MM-DD en Europe/Madrid.
    Cada registro debe pertenecer a ese día después de normalizar su instante.
    El motor actual rechaza días con cambio de hora porque representa días de 24 horas.

    Los precios deben ser int, float o Decimal finitos. Se admiten cero y
    negativos; se rechazan valores ausentes, texto y booleanos con ValueError.

    registros debe ser una lista no vacía de objetos con datetime como texto
    ISO con separador T y desplazamiento UTC explícito. Los formatos inesperados
    también producen ValueError.
    """
    dia_esperado = date.fromisoformat(fecha_esperada)
    if not isinstance(registros, list) or not registros:
        raise ValueError("Los registros PVPC deben ser una lista no vacía.")

    # El motor de horas 0–23 no puede representar con seguridad días de 23 o 25 horas.
    inicio_dia = datetime.combine(dia_esperado, time.min, tzinfo=ZONA_PENINSULAR)
    fin_dia = datetime.combine(dia_esperado, time.max, tzinfo=ZONA_PENINSULAR)
    if inicio_dia.utcoffset() != fin_dia.utcoffset():
        raise ValueError("El motor actual no admite días con cambio de hora.")

    precios = {}

    for registro in registros:
        if not isinstance(registro, dict):
            raise ValueError("Cada registro PVPC debe ser un objeto JSON.")

        fecha_hora = _normalizar_fecha_hora(registro.get("datetime"))

        # Comprobamos día y hora locales, nunca los de la representación de origen.
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
