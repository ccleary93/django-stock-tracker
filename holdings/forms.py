from django import forms
from holdings.models import Holding

class CreateForm(forms.ModelForm):
    class Meta:
        model = Holding
        fields = ['name', 'ticker', 'amt']
        
class UpdateForm(forms.ModelForm):
    class Meta:
        model = Holding
        fields = ['amt']
        