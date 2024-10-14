from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
# from django.contrib.auth.models import User
from UserAuth.models import UserProfile

# - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
The following section defines the forms which are used to create or authenticate users with the Django application.
"""

class SignUserUpForm(UserCreationForm):
    """
    The SignUserUpForm is used to create a new user within the Django application.
    """
    # Override the ModelForm's '__init__' function to redefine the attributes of the
    # widget when injecting them into the Django Template
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the attributes of the Fields
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = UserProfile
        fields = ["username", "email", "password1", "password2"]


class UserLoginForm(forms.Form):
    """
    Define the UserLoginForm users fill out when being authenticated with the application.
    """
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'})) 
    password = forms.CharField(max_length=128, widget=forms.PasswordInput(attrs={'class': 'form-control'}))