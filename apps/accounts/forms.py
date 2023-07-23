from django import forms


class LoginForm(forms.Form):
    login_with = forms.CharField()
    password = forms.CharField()
