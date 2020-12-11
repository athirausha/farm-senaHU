from django import forms 
from Base.models import Profile

class DateInput(forms.DateInput):
    input_type = 'date'

class ProfileForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    lname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    skype = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
  
    
    class Meta:
        model = Profile
        fields = ['name', 'lname', 'phone', 'skype', 'location']