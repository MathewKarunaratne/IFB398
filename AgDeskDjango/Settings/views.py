"""
The settings views. Also contains user management.
"""

# Imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from FarmAcc.forms import JoinFarmForm, NewFarm
from FarmAcc.models import FarmInfo
from FarmAcc.views import FarmManager, LinkingManager
from UserAuth.models import UserProfile, SecurityGroup, user_farm

from .forms import farmSettingsUpdate, orgSettingsForm, teamSettingsForm, userDetailsForm, UpdateProfileDetails#, userSignupForm
from .models import orgSettingsModel, internalTeamsModel, LinkingCode

import os


def farmSettings(request):
    current_user = UserProfile.objects.get(id=request.user.id)
    farm_instance = FarmInfo.objects.get(id=current_user.currentFarm_id)
    context = {
        "form"      : farmSettingsUpdate(instance=farm_instance),
        "farm_image": farm_instance.farm_image,
    }

    if request.method == "POST":
        form = farmSettingsUpdate(request.POST, request.FILES, instance=farm_instance)

        if form.is_valid():
            form.save()

            return redirect('farmSettings')

        else:
            form = farmSettingsUpdate(instance=farm_instance)

    return render(request, "Settings/farmSettings.html", context)


def orgSettings(request):
    if request.method == "POST":
        form = orgSettingsForm(request.POST)
        if form.is_valid():
            request.session["django_timezone"] = request.POST["timezone"]

            orgSettingsValues = orgSettingsModel.objects.get(id=1)
            form = orgSettingsForm(request.POST, instance=orgSettingsValues)
            form.save()

            return redirect('orgSettings')

    context = {
        "current_datetime": timezone.localtime(timezone.now()),
        "datetime_format" : orgSettingsModel.objects.get(pk=1).datetime_format,
        "form"            : orgSettingsForm()
    }

    return render(request, "Settings/orgSettings.html", context)


def profileUpdate(request):
    instance = UserProfile.objects.get(id=request.user.id)
    farmInstance = FarmInfo.objects.get(id=instance.currentFarm_id)
    user_farm = farmInstance.farm_name

    if request.method == "POST":
        form = UpdateProfileDetails(request.POST, instance=instance)
        if form.is_valid():
            form.save()

            return redirect('profileUpdate')

        else:
            form = UpdateProfileDetails(instance=instance)

    context = {
        'form'    : UpdateProfileDetails(instance=instance),
        'instance': instance,
        'farm'    : user_farm
    }

    return render(request, "Settings/profileUpdate.html", context)


def manage_farms(request):
    farmManager = FarmManager()

    # Handle "Get" requests
    user = UserProfile.objects.get(id=request.user.id)
    farm_list = farmManager.get_user_farm_assignments(user)
    current_farm = user.currentFarm_id

    context = {
        "farm_list"   : farm_list,
        "current_farm": current_farm,
        "joinFarmForm": JoinFarmForm(),
        "newFarmForm" : NewFarm()
    }

    # Handle "POST" requests
    # Allows user to join a farm using linking code
    if request.method == "POST":
        if "joinFarm" in request.POST:
            # Join a farm
            linking_manager = LinkingManager()
            form = JoinFarmForm(request.POST)

            if form.is_valid():
                # Use the linking code to join the farm
                linking_code = form.cleaned_data["linking_code"]
                linking_code_check = linking_manager.use_code(linking_code, request.user)

                # Check if the linking code is valid
                if linking_code_check:
                    return redirect("manage_farms")
                else:
                    messages.error(request, "Invalid linking code. Please try again.")

        elif "newFarm" in request.POST:
            # Create a new farm
            form = NewFarm(request.POST, request.FILES)
            if form.is_valid():
                current_user = request.user

                # Create a new farm and add it to the user's farm list
                newFarm = form.save()
                current_user.farm.add(newFarm)

                # Set the user's current farm to the new farm
                current_user.currentFarm_id = newFarm

                # Add the user to the farm owner security group
                # farmOwnerGroup = SecurityGroup.objects.get(name='Farm Owner')
                # current_user.groups.add(farmOwnerGroup)

                # Save the user
                current_user.save()

                return redirect("manage_farms")

            else:
                messages.error(request, "Error creating farm. Please try again.")

    return render(request, "Settings/manageFarms.html", context)


def switch_farm(request, farm_id):
    farmManager = FarmManager()

    # Set the user's current farm to the selected farm
    farmManager.set_user_current_farm_by_id(request.user, farm_id)

    return redirect("manage_farms")


def remove_farm(request, farm_id):
    farmManager = FarmManager()

    # Remove the farm from the user's farm list
    farmManager.remove_user_farm(request.user, farm_id)

    # Check if the user has any farms left
    user_farms = farmManager.get_user_active_farms(request.user)
    if user_farms.count() == 0:
        return redirect("joinFarm")

    else:
        # If the user has farms left, set the user's current farm to the first in the list
        farmManager.set_user_current_farm(request.user, user_farms[0])

        return redirect("manage_farms")


# The following section is used to define views concerning the 'internalTeams' model including viewing, editing,
# adding and removing teams.
@login_required(login_url='login')
def teamSettings(request: HttpRequest):
    """
    The 'teamSettings' view handles the back-end functionality associated with viewing, creating
    and deleting 'internalTeams' within the application. It retrieves a list of 'internalTeam'
    objects belonging to a certain farming tenant and renders them in a tabulated format.

    The teamSettingForm form enables additional teams to be added via the modal form in
    'teamSettings.html'
    """

    # Handle 'POST' requests (when a new internal team has been created)
    if request.method == "POST":
        form = teamSettingsForm(request.POST, request.FILES)
        if form.is_valid():
            currTeam = form.save(commit=False)
            currTeam.name = form.cleaned_data['teamName']

            # Assign the newly created team to the user's farm tenant
            currTeam.farm = FarmInfo.objects.get(pk=request.user.currentFarm_id)
            currTeam.save()

            return redirect('home', farm_id = currTeam.farm.id)

        else:
            form = teamSettingsForm()

    # Handle 'Get' Requests
    form = teamSettingsForm()
    teamList = internalTeamsModel.objects.filter(farm_id=request.user.currentFarm_id)
    context = {
        'form'    : form,
        'teamList': teamList
    }

    return render(request, "Settings/teamSettings.html", context)


@login_required(login_url='login')
def teamDetails(request: HttpRequest, team_id: int):
    """
    This view, given a team_id, will render all the details concerning the 
    the team, allowing each of the details to be edited as necessary.
    """

    # Retrieve the requested team_id
    team = internalTeamsModel.objects.get(pk=team_id)

    # Retrieve each of the users currently in the team
    currUsers = internalTeamsModel.objects.get(pk=team_id).user_set.all()

    # Pre-poopulate the form with information about the 'internalTeam' record
    initial = {
        "teamName"       : team.teamName,
        "teamDescription": team.teamDescription,
        "active"         : team.active,
        "teamImage"      : team.teamImage,
        "userList"       : currUsers
    }

    userList = UserProfile.objects.filter(currentFarm=request.user.currentFarm_id)
    form = teamSettingsForm(initial=initial, queryset=userList)     

    # Handle 'POST' requests (when a 'internalTeam' has been updated)
    if request.method == "POST":
        currTeamImg = internalTeamsModel.objects.get(id=team_id)
        form = teamSettingsForm(request.POST, request.FILES, instance=team, queryset=userList)
        if form.is_valid():
            # If an 'image_document' has been provided, remove the old file before replacing it
            if "image_document" in request.FILES:
                teamImgPth = currTeamImg.image_document.path
                if os.path.exists(teamImgPth):
                    os.remove(teamImgPth)
            internalTeam = form.save()

            # Update the users assigned to the internal teaam
            users = form.cleaned_data['userList']
            internalTeam.user_set.clear()
            for user in users:
                internalTeam.user_set.add(user)
            internalTeam.save()

            return HttpResponseRedirect(reverse('team_settings'))

    # Handle 'Get' Requests
    context = {
        "form"    : form,
        "userList": userList
    }

    return render(request, "Settings/teamDetails.html", context)


@login_required(login_url='login')
def deleteTeam(request: HttpRequest, team_id: int):
    """
    This view is used to delete the requested team_id.
    """

    team = internalTeamsModel.objects.get(id=team_id)
    team.delete()

    return HttpResponseRedirect(reverse('team_settings'))


# The following section is used to define views concerning the 'UserProfile' model including viewing, editing,
# adding and blocking users.
@login_required(login_url='login')
# @permission_required("UserAuth.can_view_other_users")
def userManagement(request: HttpRequest):
    """
    This view enables all the users beloning to a specific tenant to be viewed. Additionally,
    further users can be created within this view through the use of the modal in the
    `userManagement.html` file. 
    """

    # Handle 'POST' requests (when a new linking code has been requested)
    if request.method == "POST":
        pass
    elif request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return generate_code(request)


    # Handle 'Get' Requests
    userList = user_farm.objects.filter(farm_id=request.user.currentFarm_id).select_related('user')
    context = {
        'userList': userList
    }

    return render(request, "Settings/userManagement.html", context)


def generate_code(request):
    linking_manager = LinkingManager()
    linking_code = linking_manager.generate_code(request.user.currentFarm)
    return JsonResponse({"linking_code": linking_code})


@login_required(login_url='login')
# @permission_required("UserAuth.can_view_other_users")
def userDetails(request: HttpRequest, user_id: int):
    """
    This view enables a specific 'UserProfile' object (a user) to have its attributes updated.
    """

    # Handle 'Get' Requests
    farmManager = FarmManager()

    # Retrieve the requested user_id
    user = user_farm.objects.get(user_id=user_id, farm_id = request.user.currentFarm_id)

    # Pre-populate the form with information about the 'User' record
    form = userDetailsForm(initial=user.__dict__)

    context = {
        "form": form,
        "user": user
    }

    # Handle 'POST' requests (when a 'UserProfile' has been updated)
    if request.method == "POST":
        form = userDetailsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()

            if form.cleaned_data['is_active'] is False:
                if farmManager.get_user_active_farms(user.user).count() == 0:# or user.user.groups.filter(name='Farm Owner').exists():
                    user.user.is_active = False
                    user.user.save()

            # Update the security groups
            groups = form.cleaned_data['groups']
            securityGroups = SecurityGroup.objects.filter(name=SecurityGroup)
            for securityGroup in securityGroups:
                securityGroup.user_set.remove(user)
            for group in groups:
                user.groups.add(group)

        return render(request, "Settings/userDetails.html", context=context) # Same line as after the if

    return render(request, "Settings/userDetails.html", context=context)
