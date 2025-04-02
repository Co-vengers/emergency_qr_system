from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmergencyInfo

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EmergencyInfoForm(forms.ModelForm):
    class Meta:
        model = EmergencyInfo
        fields = ('name', 'contact_number', 'medical_conditions', 
                  'allergies', 'blood_type', 'emergency_contacts')
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'emergency_contacts': forms.Textarea(attrs={'rows': 3, 
                'placeholder': 'John Doe - Brother - 123-456-7890\nJane Smith - Mother - 098-765-4321'}),
        }