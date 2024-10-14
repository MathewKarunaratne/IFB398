"""
Views for UserAuth.
"""


# Imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required # This indicates that logging in is required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest
from django.shortcuts import render, redirect

from FarmAcc.views import FarmManager
from UserAuth.models import UserProfile

from . form import SignUserUpForm, UserLoginForm


# User Registration and Authentication
def signup(request: HttpRequest):
    """
    This view renders the sign up page which allows users to signup and create a new farming tenant.
    """

    # Disallow users to visit the signup page if they are already authenticated
    if request.user.is_authenticated:
        return render(request, "Dashboard/baseDash.html")

    # Handle 'POST' requests (when a user is signing up)
    if request.method == "POST":
        form = SignUserUpForm(request.POST)
        if form.is_valid():
            form.save()

            # Provide a success message to the user
            messages.success(
                request,
                "Account was generated for " + form.cleaned_data.get('username')
            )

            return redirect('login')

    # Handle 'Get' Requests
    form = SignUserUpForm()
    context = {
        'form': form
    }
    return render(request, 'UserAuth/signup.html', context)


def logoutUser(request: HttpRequest):
    """
    This view allows a givn user to log out from the application and redirects
    them to the login page.
    """

    logout(request)

    return redirect('login')


@login_required(login_url='login')
def adminOverview(request: HttpRequest):
    """
    This view renders the index.html file upon a successful sign-in.
    """

    return render(request, "UserAuth/index.html")


def loginPage(request: HttpRequest):
    """
    This view renders the login page, allowing users to authenticate themselves with the server.
    """

    farmManager = FarmManager()
    # Disallow users to visit the login page if they are already authenticated
    if request.user.is_authenticated:
        return render(request, "Dashboard/baseDash.html")

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            userName = form.cleaned_data["username"]
            userPassword = form.cleaned_data["password"]

        # Handle 'POST' requests (when a user is authenticating themselves)
        if UserProfile.objects.filter(username=userName).exists():
            if UserProfile.objects.get(username=userName).is_active is False:
                inactive_user = UserProfile.objects.get(username=userName)
                inactive_user.is_active = True
                inactive_user.save()

            user = authenticate(username=userName, password=userPassword)
            if user is not None:
                user_farms = farmManager.get_user_active_farms(user)
                login(request, user)

                match len(user_farms):
                    case 0:
                        return redirect("farm/join")
                    case 1:
                        return redirect('home', farm_id = user_farms[0].id)
                    case _:
                        return redirect("farm/choose-farm")

        messages.error(request, "Password or username was incorrect ")

        return redirect("login")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Handle 'Get' Requests
    form = UserLoginForm()
    context = {
        'form': form
    }
    return render(request, "UserAuth/login.html", context)
