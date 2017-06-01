from django import forms
from .models import Menu


class UploadFileForm(forms.Form):
    class Meta:
        model = Menu
        fields = ('choice_menu', )