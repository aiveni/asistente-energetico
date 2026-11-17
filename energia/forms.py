"""Datos y validaciones del formulario de búsqueda."""

from django import forms


class FranjaForm(forms.Form):
    """Recoge una fecha y un horario entero para buscar dos horas consecutivas."""

    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    )
    inicio = forms.IntegerField(
        label="Disponible desde (hora)",
        min_value=0,
        max_value=22,
        initial=18,
    )
    fin = forms.IntegerField(
        label="Disponible hasta (hora)",
        min_value=2,
        max_value=24,
        initial=22,
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
