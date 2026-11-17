"""Datos y validaciones del formulario de búsqueda."""

from django import forms
from django.utils import timezone


class FranjaForm(forms.Form):
    """Recoge una fecha y un horario entero para buscar dos horas consecutivas."""

    fecha = forms.DateField(
        label="Fecha",
        initial=timezone.localdate,
        help_text="El día para el que quieres planificar tu consumo.",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    )
    inicio = forms.TypedChoiceField(
        label="Desde",
        choices=[(hora, f"{hora:02d}:00") for hora in range(23)],
        coerce=int,
        initial=18,
        help_text="Puedes empezar a partir de esta hora.",
    )
    fin = forms.TypedChoiceField(
        label="Hasta",
        choices=[(hora, f"{hora:02d}:00") for hora in range(2, 25)],
        coerce=int,
        initial=22,
        help_text="Debes terminar antes o a esta hora. 24:00 es medianoche.",
    )

    def clean(self):
        """Valida la duración tras convertir y comprobar cada campo por separado.

        Solo compara horas que hayan superado su validación individual. El
        horario debe contener dos horas completas dentro de un mismo día.
        """
        datos = super().clean()
        inicio = datos.get("inicio")
        fin = datos.get("fin")

        if inicio is not None and fin is not None:
            if fin - inicio < 2:
                raise forms.ValidationError(
                    "El horario debe permitir al menos dos horas consecutivas."
                )

        return datos
