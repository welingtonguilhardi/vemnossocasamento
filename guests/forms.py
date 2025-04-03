from django import forms
from .models import Guest

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['name', 'companions']
        
class GuestCheckInForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['checked_in'].widget.attrs.update({
            'class': 'form-check-input',
            'role': 'switch'
        })
        self.fields['companions_checked_in'].widget.attrs.update({
            'class': 'form-control',
            'min': 0,
            'max': self.instance.companions if self.instance else 0
        })
    
    class Meta:
        model = Guest
        fields = ['checked_in', 'companions_checked_in']
        widgets = {
            'companions_checked_in': forms.NumberInput(),
        }
class GuestFilterForm(forms.Form):
    search = forms.CharField(required=False, label="Buscar por nome ou código")