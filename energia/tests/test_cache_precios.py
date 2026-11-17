"""Pruebas de reutilización y caducidad con caché real y consultas simuladas."""

from decimal import Decimal
from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from energia.cache_precios import obtener_precios_con_cache


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "energia-tests-cache-precios",
        },
    },
    PRECIOS_CACHE_TIMEOUT=300,
)
class TestCachePrecios(SimpleTestCase):
    """Comprueba que solo se reutilicen días completos durante el plazo configurado."""

    def setUp(self):
        """Aísla la caché y prepara un día completo con precios Decimal válidos."""
        cache.clear()
        self.addCleanup(cache.clear)
        self.fecha = "2026-11-15"
        self.precios = dict.fromkeys(range(24), Decimal("0.10"))

    @patch("energia.cache_precios.obtener_precios")
    def test_reutiliza_precios_de_la_misma_fecha(self, consulta):
        """Dos peticiones de la misma fecha descargan los precios una sola vez."""
        consulta.return_value = self.precios

        primera = obtener_precios_con_cache(self.fecha)
        segunda = obtener_precios_con_cache(self.fecha)

        self.assertEqual(primera, self.precios)
        self.assertEqual(segunda, self.precios)
        consulta.assert_called_once_with(self.fecha)

    @patch("energia.cache_precios.obtener_precios")
    def test_separa_fechas(self, consulta):
        """La copia de un día no se utiliza para una fecha distinta."""
        otros_precios = dict.fromkeys(range(24), Decimal("0.20"))
        consulta.side_effect = [self.precios, otros_precios]

        obtener_precios_con_cache(self.fecha)
        resultado = obtener_precios_con_cache("2026-11-16")
        repetido = obtener_precios_con_cache(self.fecha)

        self.assertEqual(resultado, otros_precios)
        self.assertEqual(repetido, self.precios)
        self.assertEqual(consulta.call_count, 2)
        consulta.assert_any_call(self.fecha)
        consulta.assert_any_call("2026-11-16")

    @patch("energia.cache_precios.obtener_precios")
    def test_respeta_caducidad_configurada_sin_renovarla_al_leer(self, consulta):
        """Leer antes de caducar no retrasa la descarga siguiente; el reloj es simulado."""
        actualizados = {**self.precios, 18: Decimal("0.25")}

        for duracion in [300, 60]:
            with self.subTest(duracion=duracion), override_settings(PRECIOS_CACHE_TIMEOUT=duracion):
                cache.clear()
                consulta.reset_mock()
                consulta.side_effect = [self.precios, actualizados]

                with patch("time.time", return_value=1000) as reloj:
                    obtener_precios_con_cache(self.fecha)
                    reloj.return_value = 1000 + duracion - 1
                    self.assertEqual(obtener_precios_con_cache(self.fecha), self.precios)
                    consulta.assert_called_once_with(self.fecha)

                    reloj.return_value = 1000 + duracion + 1
                    self.assertEqual(obtener_precios_con_cache(self.fecha), actualizados)
                    self.assertEqual(consulta.call_count, 2)

    @patch("energia.cache_precios.obtener_precios")
    def test_no_cachea_errores_de_la_consulta(self, consulta):
        """Los errores de conexión o validación permiten reintentar inmediatamente."""
        for error in [httpx.ReadTimeout("Sin respuesta"), ValueError("Datos inválidos")]:
            with self.subTest(error=type(error).__name__):
                cache.clear()
                consulta.reset_mock()
                consulta.side_effect = [error, self.precios]

                with self.assertRaises(type(error)):
                    obtener_precios_con_cache(self.fecha)

                self.assertEqual(obtener_precios_con_cache(self.fecha), self.precios)
                self.assertEqual(consulta.call_count, 2)

    @patch("energia.cache_precios.obtener_precios")
    def test_no_cachea_datos_incompletos(self, consulta):
        """Los precios parciales se devuelven, pero la siguiente petición reconsulta."""
        for parciales in [{}, {18: Decimal("0.10"), 19: Decimal("0.10")}]:
            with self.subTest(horas=list(parciales)):
                cache.clear()
                consulta.reset_mock()
                consulta.side_effect = [parciales, self.precios]

                self.assertEqual(obtener_precios_con_cache(self.fecha), parciales)
                self.assertEqual(obtener_precios_con_cache(self.fecha), self.precios)
                self.assertEqual(obtener_precios_con_cache(self.fecha), self.precios)
                self.assertEqual(consulta.call_count, 2)

    @patch("energia.cache_precios.obtener_precios")
    def test_no_usa_datos_caducados_si_falla_la_consulta(self, consulta):
        """Una caída tras caducar propaga el error en lugar de servir la copia antigua."""
        actualizados = {**self.precios, 18: Decimal("0.25")}
        consulta.side_effect = [self.precios, httpx.ReadTimeout("Sin respuesta"), actualizados]

        with patch("time.time", return_value=1000) as reloj:
            obtener_precios_con_cache(self.fecha)
            reloj.return_value = 1301

            with self.assertRaises(httpx.ReadTimeout):
                obtener_precios_con_cache(self.fecha)

            self.assertEqual(obtener_precios_con_cache(self.fecha), actualizados)
            self.assertEqual(consulta.call_count, 3)
