from django import forms
from calculator.core import parse_shutter
from calculator.scenes import SCENES


class ShutterField(forms.CharField):
    """Accepts '1/125' or '2' and returns seconds as a float."""

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return None
        try:
            seconds = parse_shutter(value)
        except (ValueError, ZeroDivisionError):
            raise forms.ValidationError("Use a value like 1/125 or 2")
        if seconds <= 0:
            raise forms.ValidationError("Must be greater than 0")
        return seconds


class ExposureForm(forms.Form):
    light = forms.TypedChoiceField(
        label="Light",
        coerce=int,
        choices=[(ev, f"{name} (EV {ev})") for ev, name in SCENES],
        initial=12,
    )
    aperture = forms.FloatField(min_value=0.5, required=False, label="Aperture f/")
    shutter = ShutterField(required=False, label="Shutter")
    iso = forms.FloatField(min_value=1, required=False, label="ISO")

    def clean(self):
        data = super().clean()
        # Skip this check if a field already failed (e.g. bad shutter text)
        if self.errors:
            return data
        settings = [data.get("aperture"), data.get("shutter"), data.get("iso")]
        if settings.count(None) != 1:
            raise forms.ValidationError(
                "Fill in two settings and leave one empty: that one gets calculated."
            )
        return data