from django import forms


class CreateConflictForm(forms.Form):

    title = forms.CharField(label='Tetstt1', max_length=128)
    type_undefind = forms.CharField(widget=(forms.RadioSelect(attrs={'type': "radio",
                                                                       'value': "undefind",
                                                                       'name': "controller_type",
                                                                       'id': "undefind"})))
