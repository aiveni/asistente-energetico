"""Pruebas del adaptador PVPC y su conexión con el motor, sin acceso a red."""

import unittest
from decimal import Decimal

from adaptador_precios import convertir_precios
from motor import buscar_mejor_franja


class TestConvertirPrecios(unittest.TestCase):
    """Verifica el contrato actual: precios horarios de un solo día."""

    def setUp(self):
        """Prepara una muestra local con los cuatro precios consultados a REData."""
        self.fecha = "2026-11-15"
        self.registros = [
            {"datetime": "2026-11-15T18:00:00.000+01:00", "value": 237.62},
            {"datetime": "2026-11-15T19:00:00.000+01:00", "value": 240.99},
            {"datetime": "2026-11-15T20:00:00.000+01:00", "value": 231.96},
            {"datetime": "2026-11-15T21:00:00.000+01:00", "value": 214.55},
        ]

    def test_convierte_a_euros_por_kwh_con_valores_decimal(self):
        """Divide entre mil y entrega las horas y precios que espera el motor."""
        precios = convertir_precios(self.registros, fecha_esperada=self.fecha)

        self.assertEqual(precios, {
            18: Decimal("0.23762"),
            19: Decimal("0.24099"),
            20: Decimal("0.23196"),
            21: Decimal("0.21455"),
        })
        for precio in precios.values():
            self.assertIsInstance(precio, Decimal)

    def test_conserva_precios_negativos_y_cero(self):
        """No redondea a cero ni elimina los precios negativos al convertirlos."""
        registros = [
            {"datetime": "2026-11-15T00:00:00.000+01:00", "value": -12.34},
            {"datetime": "2026-11-15T23:00:00.000+01:00", "value": 0},
        ]

        self.assertEqual(convertir_precios(registros, fecha_esperada=self.fecha), {
            0: Decimal("-0.01234"),
            23: Decimal("0"),
        })

    def test_rechaza_duplicados_en_vez_de_sobrescribir_el_precio(self):
        """Un segundo precio para la misma hora provoca un error explícito."""
        duplicado = {
            "datetime": "2026-11-15T18:00:00.000+01:00",
            "value": 100,
        }

        with self.assertRaisesRegex(ValueError, "horas repetidas"):
            convertir_precios(self.registros + [duplicado], fecha_esperada=self.fecha)

    def test_rechaza_hora_repetida_con_distinto_desplazamiento(self):
        """Dos instantes distintos con la misma hora local no se fusionan."""
        registros = [
            {"datetime": "2026-10-25T02:00:00.000+02:00", "value": 100},
            {"datetime": "2026-10-25T02:00:00.000+01:00", "value": 200},
        ]

        with self.assertRaisesRegex(ValueError, "horas repetidas"):
            convertir_precios(registros, fecha_esperada="2026-10-25")

    def test_rechaza_registros_fuera_de_la_hora_exacta(self):
        """Evita interpretar intervalos parciales como horas completas."""
        fechas = [
            "2026-11-15T18:15:00.000+01:00",
            "2026-11-15T18:00:01.000+01:00",
            "2026-11-15T18:00:00.001+01:00",
        ]

        for fecha in fechas:
            with self.subTest(fecha=fecha):
                registros = [{"datetime": fecha, "value": 237.62}]

                with self.assertRaisesRegex(ValueError, "inicio de cada hora"):
                    convertir_precios(registros, fecha_esperada=self.fecha)

    def test_rechaza_registros_de_otro_dia(self):
        """No mezcla precios de otra fecha con los del día solicitado."""
        fechas = [
            "2026-11-14T22:00:00.000+01:00",
            "2026-11-16T22:00:00.000+01:00",
            "2026-12-15T22:00:00.000+01:00",
            "2025-11-15T22:00:00.000+01:00",
        ]

        for fecha in fechas:
            with self.subTest(fecha=fecha):
                registro_ajeno = {"datetime": fecha, "value": 100}

                with self.assertRaisesRegex(ValueError, "día solicitado"):
                    convertir_precios(
                        self.registros + [registro_ajeno],
                        fecha_esperada=self.fecha,
                    )

    def test_muestra_convertida_produce_la_franja_verificada_a_mano(self):
        """Adaptador y motor eligen 20–22 con un coste de 0,44651 euros a 1 kW."""
        precios = convertir_precios(self.registros, fecha_esperada=self.fecha)

        resultado = buscar_mejor_franja(precios, inicio=18, fin=22)

        self.assertEqual(resultado, (20, Decimal("0.44651")))
