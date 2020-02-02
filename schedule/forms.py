from django import forms


class WilmaURLForm(forms.Form):
    url = forms.URLField(label='', max_length=500)
