# Dans forms.py
from django import forms
from .models import Equipement, Client

class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ('name', 'state', 'category', 'image')

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('name', 'email', 'phone', 'message', 'adresse', 'image')