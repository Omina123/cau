from .models import *
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ZakaForm(forms.ModelForm):
    class Meta:
        model= Zaka
        fields='__all__'
class MavunoForm(forms.ModelForm):
    class Meta:
        model= Mavuno
        fields='__all__'
class SpecialForm(forms.ModelForm):
    class Meta:
        model= SpecialContribution
        fields='__all__'

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['parish', 'outstation', 'jumuiya', 'group', 'full_name', 'phone_number']
        widgets = {
            'parish': forms.Select(attrs={'id': 'parish'}),
            'outstation': forms.Select(attrs={'id': 'outstation'}),
            'jumuiya': forms.Select(attrs={'id': 'jumuiya'}),
        }
class OutstationForm(forms.ModelForm):
    class Meta:
        model = Outstation
        fields = ['name', 'parish']
class JumuiyaForm(forms.ModelForm):
    class Meta:
        model = Jumuiya
        fields = ['name', 'outstation']

class SadakaForm(forms.ModelForm):
    class Meta:
        model = Sadaka
        fields = ['outstation', 'amount', 'date_recorded']