"""Pruebas HTTP del formulario, el resultado y los errores con datos simulados."""

import json
from decimal import Decimal
from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "energia-tests-vistas",
    },
})
class TestInicio(SimpleTestCase):
    """Comprueba búsquedas válidas, validación, fallos de datos y reintentos."""

    def setUp(self):
        """Prepara los parámetros de una búsqueda con fecha y horas conocidas."""
        cache.clear()
        self.addCleanup(cache.clear)
        self.busqueda = {
            "fecha": "2026-11-15",
            "inicio": "18",
            "fin": "22",
        }

    def _comprobar_error_sin_resultado(self, respuesta, mensaje):
        """Exige un error visible, los campos conservados y ninguna recomendación."""
        self.assertContains(respuesta, mensaje)
        self.assertNotContains(respuesta, "Franja recomendada")
        self.assertIsNone(respuesta.context["resultado"])

        formulario = respuesta.context["formulario"]
        self.assertEqual(list(formulario.non_field_errors()), [mensaje])
        for campo, valor in self.busqueda.items():
            with self.subTest(campo=campo):
                self.assertEqual(formulario[campo].value(), valor)
                self.assertContains(respuesta, f'value="{valor}"')

    def _respuesta_pvpc(self, registros):
        """Construye una respuesta de REData para probar el recorrido completo sin red."""
        return httpx.Response(
            200,
            json={"included": [{"id": "1001", "attributes": {"values": registros}}]},
            request=httpx.Request("GET", "https://apidatos.ree.es"),
        )

    def _registros_dia_completo(self):
        """Prepara 24 precios ficticios con franjas distintas para dos horarios."""
        precios = dict.fromkeys(range(24), 500)
        precios.update({
            10: 100, 11: 110,
            18: 237.62, 19: 240.99, 20: 231.96, 21: 214.55,
        })
        return [
            {"datetime": f"2026-11-15T{hora:02d}:00:00+01:00", "value": precio}
            for hora, precio in precios.items()
        ]

    @patch("energia.views.obtener_precios_con_cache")
    def test_muestra_formulario_sin_consultar_api(self, consulta):
        """Abrir la página muestra la plantilla sin solicitar precios a REData."""
        respuesta = self.client.get(reverse("inicio"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "energia/inicio.html")
        self.assertFalse(respuesta.context["formulario"].is_bound)
        consulta.assert_not_called()

    @patch("energia.views.obtener_precios_con_cache")
    def test_muestra_la_mejor_franja(self, consulta):
        """Una búsqueda válida muestra 20–22 y 0,44651 euros con precios de muestra."""
        consulta.return_value = {
            18: Decimal("0.23762"),
            19: Decimal("0.24099"),
            20: Decimal("0.23196"),
            21: Decimal("0.21455"),
        }

        respuesta = self.client.get(reverse("inicio"), self.busqueda)

        self.assertEqual(respuesta.status_code, 200)
        resultado = respuesta.context["resultado"]
        self.assertEqual(resultado["inicio"], 20)
        self.assertEqual(resultado["fin"], 22)
        self.assertEqual(resultado["coste"], Decimal("0.44651"))
        consulta.assert_called_once_with("2026-11-15")

    @patch("energia.views.obtener_precios_con_cache")
    def test_horario_corto_no_consulta_api(self, consulta):
        """Un horario de una hora muestra el error antes de consultar precios."""
        self.busqueda["inicio"] = "21"

        respuesta = self.client.get(reverse("inicio"), self.busqueda)

        self.assertContains(
            respuesta,
            "El horario debe permitir al menos dos horas consecutivas.",
        )
        self.assertIsNone(respuesta.context["resultado"])
        consulta.assert_not_called()

    @patch("energia.views.obtener_precios_con_cache")
    def test_error_http_muestra_mensaje_y_conserva_busqueda(self, consulta):
        """Los fallos de conexión, timeout y estado HTTP muestran un mensaje útil."""
        solicitud = httpx.Request("GET", "https://apidatos.ree.es")
        respuesta_api = httpx.Response(503, request=solicitud)
        errores = [
            httpx.ConnectError("No se puede conectar", request=solicitud),
            httpx.ReadTimeout("Tiempo de espera agotado", request=solicitud),
            httpx.HTTPStatusError(
                "Servicio no disponible", request=solicitud, response=respuesta_api
            ),
        ]

        for error in errores:
            with self.subTest(error=type(error).__name__):
                consulta.reset_mock()
                consulta.side_effect = error

                respuesta = self.client.get(reverse("inicio"), self.busqueda)

                self._comprobar_error_sin_resultado(
                    respuesta,
                    "No hemos podido consultar los precios. Inténtalo de nuevo.",
                )
                consulta.assert_called_once_with("2026-11-15")

    @patch("energia.views.obtener_precios_con_cache")
    def test_error_de_datos_muestra_mensaje_y_conserva_busqueda(self, consulta):
        """Un fallo de validación del servicio muestra el error general de datos."""
        consulta.side_effect = ValueError("Los precios no pertenecen al día solicitado.")

        respuesta = self.client.get(reverse("inicio"), self.busqueda)

        self._comprobar_error_sin_resultado(
            respuesta,
            "No hay datos horarios utilizables para esa fecha y horario.",
        )
        consulta.assert_called_once_with("2026-11-15")

    @patch("energia.views.obtener_precios_con_cache")
    def test_precios_ausentes_no_muestran_recomendacion(self, consulta):
        """El motor real rechaza precios vacíos o incompletos y la web informa."""
        muestras = [
            {},
            {
                18: Decimal("0.23762"),
                19: Decimal("0.24099"),
                21: Decimal("0.21455"),
            },
        ]

        for precios in muestras:
            with self.subTest(horas_disponibles=list(precios)):
                consulta.reset_mock()
                consulta.return_value = precios

                respuesta = self.client.get(reverse("inicio"), self.busqueda)

                self._comprobar_error_sin_resultado(
                    respuesta,
                    "No hay datos horarios utilizables para esa fecha y horario.",
                )
                consulta.assert_called_once_with("2026-11-15")

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_precio_invalido_de_api_muestra_error_sin_recomendacion(self, consulta):
        """La consulta y el adaptador reales rechazan precios inválidos en la web."""
        contenido = """
        {"included": [{"id": "1001", "attributes": {"values": [
            {"datetime": "2026-11-15T18:00:00+01:00", "value": 237.62},
            {"datetime": "2026-11-15T19:00:00+01:00", "value": 240.99},
            {"datetime": "2026-11-15T20:00:00+01:00", "value": PRECIO_INVALIDO},
            {"datetime": "2026-11-15T21:00:00+01:00", "value": 214.55}
        ]}}]}
        """
        # 1e999 es un número JSON que el lector convierte en un float infinito.
        for valor_json in ["null", '"sin precio"', "true", "1e999", "-1e999"]:
            with self.subTest(valor_json=valor_json):
                consulta.reset_mock()
                consulta.return_value = httpx.Response(
                    200,
                    text=contenido.replace("PRECIO_INVALIDO", valor_json),
                    request=httpx.Request("GET", "https://apidatos.ree.es"),
                )

                respuesta = self.client.get(reverse("inicio"), self.busqueda)

                self._comprobar_error_sin_resultado(
                    respuesta,
                    "No hay datos horarios utilizables para esa fecha y horario.",
                )
                consulta.assert_called_once()

    @patch("energia.views.obtener_precios_con_cache")
    def test_busqueda_puede_repetirse_tras_un_fallo(self, consulta):
        """Una segunda búsqueda correcta sustituye el error por la recomendación."""
        consulta.side_effect = [
            httpx.ReadTimeout("Tiempo de espera agotado"),
            {
                18: Decimal("0.23762"),
                19: Decimal("0.24099"),
                20: Decimal("0.23196"),
                21: Decimal("0.21455"),
            },
        ]

        primera = self.client.get(reverse("inicio"), self.busqueda)
        self._comprobar_error_sin_resultado(
            primera,
            "No hemos podido consultar los precios. Inténtalo de nuevo.",
        )

        segunda = self.client.get(reverse("inicio"), self.busqueda)

        self.assertContains(segunda, "Franja recomendada")
        self.assertFalse(segunda.context["formulario"].errors)
        self.assertEqual(segunda.context["resultado"]["inicio"], 20)
        self.assertEqual(segunda.context["resultado"]["coste"], Decimal("0.44651"))
        self.assertEqual(consulta.call_count, 2)

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_respuesta_malformada_muestra_error_sin_recomendacion(self, consulta):
        """Un cuerpo inválido recorre consulta y adaptador sin provocar un error 500."""
        datos_invalidos = [
            None,
            {},
            {"included": None},
            {"included": [None]},
            {"included": [{"id": "1001", "attributes": None}]},
            {"included": [{"id": "1001", "attributes": {"values": {}}}]},
            {"included": [{"id": "1001", "attributes": {"values": []}}]},
            {"included": [{"id": "1001", "attributes": {"values": [None]}}]},
            {"included": [{"id": "1001", "attributes": {"values": [
                {"value": 100},
            ]}}]},
            {"included": [{"id": "1001", "attributes": {"values": [
                {"datetime": None, "value": 100},
            ]}}]},
        ]
        contenidos = ["", "<html>Servicio no disponible</html>"]
        contenidos += [json.dumps(datos) for datos in datos_invalidos]

        for contenido in contenidos:
            with self.subTest(contenido=contenido):
                consulta.reset_mock()
                consulta.return_value = httpx.Response(
                    200,
                    text=contenido,
                    request=httpx.Request("GET", "https://apidatos.ree.es"),
                )

                respuesta = self.client.get(reverse("inicio"), self.busqueda)

                self._comprobar_error_sin_resultado(
                    respuesta,
                    "No hay datos horarios utilizables para esa fecha y horario.",
                )
                consulta.assert_called_once()

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_resultado_usa_horas_de_madrid_con_respuesta_utc(self, consulta):
        """La página muestra la franja local correcta a partir de precios fechados en UTC."""
        consulta.return_value = self._respuesta_pvpc([
            {"datetime": f"2026-11-15T{hora}:00:00Z", "value": precio}
            for hora, precio in [(17, 237.62), (18, 240.99), (19, 231.96), (20, 214.55)]
        ])

        respuesta = self.client.get(reverse("inicio"), self.busqueda)

        self.assertContains(respuesta, "Franja recomendada")
        self.assertContains(respuesta, "Europe/Madrid")
        resultado = respuesta.context["resultado"]
        self.assertEqual(resultado["fecha"].isoformat(), self.busqueda["fecha"])
        self.assertEqual(resultado["inicio"], 20)
        self.assertEqual(resultado["fin"], 22)
        self.assertEqual(resultado["coste"], Decimal("0.44651"))

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_datos_sin_zona_muestran_error(self, consulta):
        """Una marca temporal sin desplazamiento no produce una recomendación ambigua."""
        consulta.return_value = self._respuesta_pvpc([
            {"datetime": f"2026-11-15T{hora}:00:00", "value": 100}
            for hora in range(18, 22)
        ])

        respuesta = self.client.get(reverse("inicio"), self.busqueda)

        self._comprobar_error_sin_resultado(
            respuesta, "No hay datos horarios utilizables para esa fecha y horario."
        )

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_dias_con_cambio_de_hora_muestran_error(self, consulta):
        """Los días no admitidos conservan la búsqueda e informan de la limitación."""
        for fecha in ["2026-03-29", "2026-10-25"]:
            with self.subTest(fecha=fecha):
                self.busqueda["fecha"] = fecha
                consulta.return_value = self._respuesta_pvpc([
                    {"datetime": f"{fecha}T{hora}:00:00Z", "value": 100}
                    for hora in range(16, 21)
                ])

                respuesta = self.client.get(reverse("inicio"), self.busqueda)

                self._comprobar_error_sin_resultado(
                    respuesta, "No hay datos horarios utilizables para esa fecha y horario."
                )
                self.assertContains(respuesta, "días con cambio de hora")

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_cambiar_horario_reutiliza_precios_del_dia(self, consulta):
        """Dos horarios calculan franjas distintas usando una sola descarga diaria."""
        consulta.return_value = self._respuesta_pvpc(self._registros_dia_completo())

        primera = self.client.get(reverse("inicio"), self.busqueda)
        segunda = self.client.get(
            reverse("inicio"), {**self.busqueda, "inicio": "10", "fin": "13"}
        )

        self.assertContains(primera, "Franja recomendada")
        self.assertEqual(primera.context["resultado"]["inicio"], 20)
        self.assertEqual(primera.context["resultado"]["coste"], Decimal("0.44651"))
        self.assertContains(segunda, "Franja recomendada")
        self.assertEqual(segunda.context["resultado"]["inicio"], 10)
        self.assertEqual(segunda.context["resultado"]["fin"], 12)
        self.assertEqual(segunda.context["resultado"]["coste"], Decimal("0.21"))
        consulta.assert_called_once()

    @patch("energia.servicios.consultar_precios.httpx.get")
    def test_precios_incompletos_se_reconsultan_en_la_web(self, consulta):
        """Una respuesta parcial no impide recuperar el día completo al reintentar."""
        registros = self._registros_dia_completo()
        consulta.side_effect = [
            self._respuesta_pvpc(registros[18:20]),
            self._respuesta_pvpc(registros),
        ]

        primera = self.client.get(reverse("inicio"), self.busqueda)
        self._comprobar_error_sin_resultado(
            primera, "No hay datos horarios utilizables para esa fecha y horario."
        )

        segunda = self.client.get(reverse("inicio"), self.busqueda)
        tercera = self.client.get(reverse("inicio"), self.busqueda)

        self.assertContains(segunda, "Franja recomendada")
        self.assertEqual(segunda.context["resultado"]["coste"], Decimal("0.44651"))
        self.assertContains(tercera, "Franja recomendada")
        self.assertEqual(tercera.context["resultado"], segunda.context["resultado"])
        self.assertEqual(consulta.call_count, 2)
