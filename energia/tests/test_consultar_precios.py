"""Pruebas de la consulta REData con respuestas simuladas, sin usar internet."""

import unittest
from decimal import Decimal
from unittest.mock import patch

import httpx

from energia.servicios.consultar_precios import URL, obtener_precios


class TestObtenerPrecios(unittest.TestCase):
    """Comprueba qué se solicita a la API y cómo se propagan sus errores."""

    def setUp(self):
        """Prepara una petición local para construir respuestas de HTTPX."""
        self.solicitud = httpx.Request("GET", URL)

    def test_consulta_la_fecha_y_devuelve_el_pvpc_convertido(self):
        """Selecciona el PVPC aunque no sea la primera serie de la respuesta."""
        for fecha, identificador in [("2026-11-15", "1001"), ("2026-11-16", 1001)]:
            with self.subTest(fecha=fecha, identificador=identificador):
                datos = {
                    "data": {},
                    "included": [
                        {
                            "id": "9999",
                            "attributes": {
                                "values": [
                                    {"datetime": f"{fecha}T18:00:00+01:00", "value": 1},
                                ],
                            },
                        },
                        {
                            "id": identificador,
                            "attributes": {
                                "values": [
                                    {"datetime": f"{fecha}T18:00:00+01:00", "value": 237.62},
                                    {"datetime": f"{fecha}T19:00:00+01:00", "value": 240.99},
                                ],
                            },
                        },
                    ],
                }
                respuesta = httpx.Response(200, json=datos, request=self.solicitud)

                # Sustituimos la llamada HTTP, manteniendo la conversión real.
                with patch("energia.servicios.consultar_precios.httpx.get", return_value=respuesta) as consulta:
                    precios = obtener_precios(fecha)

                self.assertEqual(precios, {
                    18: Decimal("0.23762"),
                    19: Decimal("0.24099"),
                })
                consulta.assert_called_once_with(
                    URL,
                    params={
                        "start_date": f"{fecha}T00:00",
                        "end_date": f"{fecha}T23:59",
                        "time_trunc": "hour",
                        "geo_trunc": "electric_system",
                        "geo_limit": "peninsular",
                        "geo_ids": "8741",
                    },
                    timeout=20,
                )

    def test_rechaza_respuesta_sin_serie_pvpc(self):
        """No devuelve precios de otra serie ni un éxito falso si falta PVPC."""
        for series in [[], [{"id": "9999", "attributes": {"values": []}}]]:
            with self.subTest(series=series):
                respuesta = httpx.Response(
                    200,
                    json={"data": {}, "included": series},
                    request=self.solicitud,
                )

                with patch("energia.servicios.consultar_precios.httpx.get", return_value=respuesta):
                    with self.assertRaisesRegex(ValueError, "no contiene la serie PVPC"):
                        obtener_precios("2026-11-15")

    def test_propaga_error_http(self):
        """Un estado 503 detiene la consulta antes de intentar leer precios."""
        respuesta = httpx.Response(503, text="Servicio no disponible", request=self.solicitud)

        with patch("energia.servicios.consultar_precios.httpx.get", return_value=respuesta):
            with self.assertRaises(httpx.HTTPStatusError) as error:
                obtener_precios("2026-11-15")

        self.assertEqual(error.exception.response.status_code, 503)

    def test_propaga_tiempo_de_espera_agotado(self):
        """Un timeout llega a quien llama para que pueda informar del fallo."""
        error = httpx.ReadTimeout("Tiempo de espera agotado", request=self.solicitud)

        # side_effect hace que la llamada simulada lance el error, sin esperar.
        with patch("energia.servicios.consultar_precios.httpx.get", side_effect=error):
            with self.assertRaises(httpx.ReadTimeout):
                obtener_precios("2026-11-15")
