from django import forms
from . import models


class ServerForm(forms.ModelForm):
    class Meta:
        model = models.Server
        fields = ['host_ip', 'username', 'password']

        widgets = {
            'host_ip': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
        }
