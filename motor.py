"""Motor del planificador energético con un ejemplo de precios ficticios.

Calcula la franja de dos horas consecutivas más barata sin depender de Django
ni de internet. El ejemplo se ejecuta solo al lanzar este archivo directamente.
"""
from decimal import Decimal

precios = {
    18: Decimal("0.20"),
    19: Decimal("0.12"),
    20: Decimal("0.08"),
    21: Decimal("0.15"),
}

def buscar_mejor_franja(tarifas, inicio, fin):
    """Devuelve la pareja de horas consecutivas más barata del horario indicado.

    Args:
        tarifas: Diccionario de horas de inicio enteras a precios Decimal en
            euros/kWh. La clave 18 representa el tramo de 18:00 a 19:00.
        inicio: Hora entera de inicio del horario permitido, incluida.
        fin: Hora entera del límite final, excluida, como máximo 24.

    Returns:
        Tupla (hora_de_inicio, coste_en_euros). El coste supone un aparato de
        1 kW constante durante dos horas, sin otros conceptos de factura.
        Si varias franjas empatan, se devuelve la que empieza antes.

    Raises:
        ValueError: Si el horario no cumple 0 <= inicio < fin <= 24,
            permite menos de dos horas o falta algún precio del horario.

    El cálculo se limita a horas enteras de un mismo día; no cruza medianoche
    ni representa cambios de hora. La franja termina dos horas tras su inicio.
    """
    mejor_inicio = None
    menor_coste = None

    if not 0 <= inicio < fin <= 24:
        raise ValueError("El horario debe estar entre 0 y 24, dentro del mismo día.")

    if fin - inicio < 2:
        raise ValueError("El horario debe permitir al menos dos horas consecutivas.")

    for hora in range(inicio, fin):
        if hora not in tarifas:
            raise ValueError(f"Falta el precio de la hora {hora}:00.")

    for hora in range(inicio, fin - 1):
        coste = tarifas[hora] + tarifas[hora + 1]

        if menor_coste is None or coste < menor_coste:
            menor_coste = coste
            mejor_inicio = hora

    return mejor_inicio, menor_coste


if __name__ == "__main__":
    hora_elegida, coste_elegido = buscar_mejor_franja(
        precios,
        inicio=18,
        fin=22,
    )

    print(
        f"Mejor franja: {hora_elegida}:00–{hora_elegida + 2}:00. "
        f"Coste: {coste_elegido} euros"
    )
