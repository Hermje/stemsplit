from django import forms

class YoutubeLinkForm(forms.Form):
    link = forms.CharField()
