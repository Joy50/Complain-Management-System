from django import forms
from .models import Complain

class ComplainForm(forms.ModelForm):
    problem_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = Complain
        fields = [
            'software', 
            'organization', 
            'referred_by', 
            'problem_description', 
            'attached_document'
        ]
        widgets = {
            'software': forms.Select(attrs={'class': 'form-select'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'referred_by': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ComplainUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Complain.STATUS_CHOICE, widget=forms.Select(attrs={'class': 'form-select'}))
    problem_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,'class': 'form-control'}),
        required=True
    )
    
    class Meta:
        model = Complain
        fields = [
            'software', 
            'organization', 
            'referred_by', 
            'problem_description', 
            'attached_document',
            'status'
        ]
        widgets = {
            'software': forms.Select(attrs={'class': 'form-select'}),
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'referred_by': forms.TextInput(attrs={'class': 'form-control'}),
        }