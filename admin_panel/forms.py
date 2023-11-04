from django import forms

from admin_panel.models import Declaration


class DeclarationForm(forms.ModelForm):
    class Meta:
        fields = ('file',)
        model = Declaration
        widgets = {
            'file': forms.FileInput(attrs={'class': 'declaration_file d-none'})
        }
