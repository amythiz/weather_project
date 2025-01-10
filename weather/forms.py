from django import forms

class CityForm(forms.Form):
    city = forms.CharField(label="", 
                           max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Город'}))
    fareng = forms.BooleanField(required=False)
            