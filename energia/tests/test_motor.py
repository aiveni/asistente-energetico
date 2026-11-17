"""Pruebas del cálculo de franjas con precios ficticios y sin acceso a red."""

import unittest
from decimal import Decimal

from energia.servicios.motor import buscar_mejor_franja


class TestBuscarMejorFranja(unittest.TestCase):
    """Comprueba la elección de franja y el respeto del horario permitido."""

    def setUp(self):
        """Prepara un diccionario de precios independiente para cada prueba."""
        self.precios = {
            18: Decimal("0.20"),
            19: Decimal("0.12"),
            20: Decimal("0.08"),
            21: Decimal("0.15"),
        }

    def test_elige_la_pareja_mas_barata(self):
        """Entre las 18 y las 22, elige 19–21 con un coste de 0,20 euros."""
        resultado = buscar_mejor_franja(self.precios, 18, 22)

        self.assertEqual(resultado, (19, Decimal("0.20")))

    def test_respeta_el_horario(self):
        """Elige 20–22 cuando la franja global más barata queda fuera del horario."""
        resultado = buscar_mejor_franja(self.precios, 20, 22)

        self.assertEqual(resultado, (20, Decimal("0.23")))

    def test_rechaza_un_horario_demasiado_corto(self):
        """Exige un horario que permita completar dos horas consecutivas."""
        with self.assertRaises(ValueError):
            buscar_mejor_franja(self.precios, 18, 19)

    def test_no_junta_horas_separadas(self):
        """No combina dos horas baratas que no sean consecutivas."""
        precios = {
            18: Decimal("0.01"),
            19: Decimal("0.50"),
            20: Decimal("0.40"),
            21: Decimal("0.02"),
        }

        resultado = buscar_mejor_franja(precios, 18, 22)

        self.assertEqual(resultado, (20, Decimal("0.42")))

    def test_en_empate_elige_la_primera_franja(self):
        """Conserva la franja más temprana cuando los costes empatan."""
        precios = {
            18: Decimal("0.10"),
            19: Decimal("0.10"),
            20: Decimal("0.10"),
        }

        resultado = buscar_mejor_franja(precios, 18, 21)

        self.assertEqual(resultado, (18, Decimal("0.20")))

    def test_rechaza_precios_incompletos(self):
        """Rechaza el cálculo si falta un precio del horario solicitado."""
        del self.precios[20]

        with self.assertRaises(ValueError):
            buscar_mejor_franja(self.precios, 18, 22)
