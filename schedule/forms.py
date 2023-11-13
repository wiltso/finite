from django import forms


class WilmaURLForm(forms.Form):
    url = forms.URLField(label='', max_length=500, required=False)
    file = forms.FileField(label="", required=False)
