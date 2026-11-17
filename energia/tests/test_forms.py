"""Pruebas de los selectores horarios y su conversión a enteros para el motor."""

from django.test import SimpleTestCase

from energia.forms import FranjaForm


class TestFranjaForm(SimpleTestCase):
    """Mantiene el contrato horario al presentar las opciones como horas legibles."""

    def test_horas_seleccionadas_se_convierten_a_enteros(self):
        """Los límites válidos, incluido terminar a las 24, entregan enteros."""
        for inicio, fin in [("0", "2"), ("22", "24"), ("18", "22")]:
            with self.subTest(inicio=inicio, fin=fin):
                formulario = FranjaForm({"fecha": "2026-11-15", "inicio": inicio, "fin": fin})

                self.assertTrue(formulario.is_valid(), formulario.errors.as_text())
                self.assertEqual(formulario.cleaned_data["inicio"], int(inicio))
                self.assertEqual(formulario.cleaned_data["fin"], int(fin))
                self.assertIsInstance(formulario.cleaned_data["inicio"], int)
                self.assertIsInstance(formulario.cleaned_data["fin"], int)

    def test_rechaza_horas_fuera_de_las_opciones(self):
        """Modificar manualmente la URL no permite horas fuera de rango o fraccionarias."""
        casos = [
            ("-1", "22", "inicio"), ("23", "24", "inicio"),
            ("18", "25", "fin"), ("18", "1", "fin"),
            ("18.5", "22", "inicio"), ("texto", "22", "inicio"),
        ]

        for inicio, fin, campo in casos:
            with self.subTest(inicio=inicio, fin=fin):
                formulario = FranjaForm({"fecha": "2026-11-15", "inicio": inicio, "fin": fin})

                self.assertFalse(formulario.is_valid())
                self.assertIn(campo, formulario.errors)

    def test_rechaza_horario_corto_invertido_o_vacio(self):
        """Las opciones válidas por separado deben permitir dos horas en orden."""
        for inicio, fin in [("18", "19"), ("22", "18"), ("18", "18")]:
            with self.subTest(inicio=inicio, fin=fin):
                formulario = FranjaForm({"fecha": "2026-11-15", "inicio": inicio, "fin": fin})

                self.assertFalse(formulario.is_valid())
                self.assertIn("__all__", formulario.errors)
