"""Pruebas del recorrido web con precios simulados y sin acceso a red."""

from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse


class TestInicio(SimpleTestCase):
    """Comprueba la página inicial, el resultado y el rechazo de un horario corto."""

    def setUp(self):
        """Prepara los parámetros de una búsqueda con fecha y horas conocidas."""
        self.busqueda = {
            "fecha": "2026-11-15",
            "inicio": "18",
            "fin": "22",
        }

    @patch("energia.views.obtener_precios")
    def test_muestra_formulario_sin_consultar_api(self, consulta):
        """Abrir la página muestra la plantilla sin solicitar precios a REData."""
        respuesta = self.client.get(reverse("inicio"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "energia/inicio.html")
        self.assertFalse(respuesta.context["formulario"].is_bound)
        consulta.assert_not_called()

    @patch("energia.views.obtener_precios")
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

    @patch("energia.views.obtener_precios")
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
