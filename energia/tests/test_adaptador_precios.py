"""Pruebas del adaptador PVPC y su conexión con el motor, sin acceso a red."""

import unittest
from decimal import Decimal

from energia.servicios.adaptador_precios import convertir_precios
from energia.servicios.motor import buscar_mejor_franja


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

    def test_rechaza_contenedor_de_registros_invalido(self):
        """Exige una lista no vacía para evitar resultados parciales o ambiguos."""
        for registros in [None, {}, "", "PVPC", 0, True, (), []]:
            with self.subTest(registros=registros):
                with self.assertRaises(ValueError):
                    convertir_precios(registros, fecha_esperada=self.fecha)

    def test_rechaza_registros_que_no_son_objetos(self):
        """Un registro inesperado invalida la muestra aunque otros sean correctos."""
        for registro in [None, [], "registro", 18, True]:
            with self.subTest(registro=registro):
                with self.assertRaises(ValueError):
                    convertir_precios(
                        self.registros + [registro], fecha_esperada=self.fecha
                    )

    def test_rechaza_fecha_hora_ausente_o_no_textual(self):
        """datetime debe existir como texto antes de intentar interpretar su fecha."""
        registros = [{"value": 100}]
        registros += [
            {"datetime": valor, "value": 100}
            for valor in [None, 123, True, [], {}]
        ]

        for registro in registros:
            with self.subTest(registro=registro):
                with self.assertRaisesRegex(ValueError, "fecha y hora"):
                    convertir_precios([registro], fecha_esperada=self.fecha)

    def test_rechaza_fecha_hora_de_formato_invalido(self):
        """Rechaza fechas sin hora y marcas temporales que no cumplen el formato."""
        fechas = [
            "", "no es una fecha", "2026-11-15", "15/11/2026 18:00",
            "2026-11-15T25:00:00+01:00", "2026-13-15T18:00:00+01:00",
        ]

        for fecha in fechas:
            with self.subTest(fecha=fecha):
                registro = {"datetime": fecha, "value": 100}

                with self.assertRaisesRegex(ValueError, "fecha y hora"):
                    convertir_precios([registro], fecha_esperada=self.fecha)

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

    def test_admite_precios_enteros_y_decimal_sin_redondear(self):
        """Admite tipos numéricos y conserva los decimales al cambiar de unidad."""
        casos = [
            (237, Decimal("0.237")),
            (Decimal("237.62001"), Decimal("0.23762001")),
        ]

        for valor, esperado in casos:
            with self.subTest(valor=valor):
                registro = {**self.registros[0], "value": valor}

                self.assertEqual(
                    convertir_precios([registro], fecha_esperada=self.fecha),
                    {18: esperado},
                )

    def test_rechaza_registro_sin_precio(self):
        """La ausencia de value produce un error de datos que la vista puede tratar."""
        registro = {"datetime": self.registros[0]["datetime"]}

        with self.assertRaisesRegex(ValueError, "precio numérico"):
            convertir_precios([registro], fecha_esperada=self.fecha)

    def test_rechaza_valores_no_numericos(self):
        """Rechaza null, texto, booleanos y estructuras en lugar de un número JSON."""
        valores = [None, "", "sin precio", "237.62", True, False, [], {}]

        for valor in valores:
            with self.subTest(valor=valor):
                registro = {**self.registros[0], "value": valor}

                with self.assertRaisesRegex(ValueError, "precio numérico"):
                    convertir_precios([registro], fecha_esperada=self.fecha)

    def test_rechaza_precios_no_finitos(self):
        """NaN e infinitos se rechazan antes de dividir o comparar costes."""
        valores = [
            float("nan"),
            float("inf"),
            float("-inf"),
            Decimal("NaN"),
            Decimal("sNaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
        ]

        for valor in valores:
            with self.subTest(valor=valor):
                registro = {**self.registros[0], "value": valor}

                with self.assertRaisesRegex(ValueError, "finitos"):
                    convertir_precios([registro], fecha_esperada=self.fecha)

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
