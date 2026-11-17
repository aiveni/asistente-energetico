"""Reutiliza precios diarios desde Django sin acoplar los servicios a la web."""

from django.conf import settings
from django.core.cache import cache

from .servicios.consultar_precios import obtener_precios


def obtener_precios_con_cache(fecha):
    """Devuelve precios validados de la fecha, reutilizando un día completo vigente.

    La vista entrega fecha en formato YYYY-MM-DD. La clave identifica el PVPC
    peninsular, su zona y la versión del formato. La duración se configura en
    PRECIOS_CACHE_TIMEOUT y no se renueva al leer. Cada horario se calcula aparte.

    Los errores se propagan sin guardarse. Los precios parciales se devuelven al
    motor para comprobar la búsqueda, pero no se guardan para futuras peticiones.
    """
    clave = f"pvpc:1001:8741:Europe-Madrid:v1:{fecha}"
    precios = cache.get(clave)
    if precios is not None:
        return precios

    precios = obtener_precios(fecha)
    # El servicio ya valida tipos, fechas y unidades; solo cacheamos días completos.
    if set(precios) == set(range(24)):
        cache.set(clave, precios, timeout=settings.PRECIOS_CACHE_TIMEOUT)

    return precios
