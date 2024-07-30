from django import forms


class CreateConflictForm(forms.Form):
    pass
    title = forms.CharField(max_length=128)
