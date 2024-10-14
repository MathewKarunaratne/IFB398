"""
Views for assetOperations, including check out / check in, operation logs ans performance metrics.
"""


# Imports
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from assetManagement.models import asset
from assetManagement.views import AssetStructures
from UserAuth.models import UserProfile

from .models import OperationLog
from .forms import checkOutForm, checkInForm
from django.contrib import messages

# Contants
MAX_NOTES_HEAD = 20

def get_user_current_checkouts(user_id):
    """
    Function to get the current checkouts for a user.
    """

    return OperationLog.objects.filter(
        userID=user_id,
        endDateTime__isnull=True,
        deleted=False
    )

def get_user_current_checkouts_oldest(user_id):
    three_oldest_logs = OperationLog.objects.filter(
        userID=user_id,
        endDateTime__isnull=True,
        deleted=False
    ).order_by('startDateTime')[:3]

    return three_oldest_logs

# Check Out / Check In``
@login_required(login_url="login")
def checkout(request):
    """
    Endpoint for checking out equipment.
    Form implemented in /assetManagement/templates/assetManagement/assetOverview.html
    """

    if request.method == "POST":
        # Replace assetID with asset instance
        # POST_dict = request.POST.copy()
        # POST_dict["assetID"] = asset.objects.get(assetID=int(POST_dict["assetID"][0]))
        # request.POST = POST_dict

        # log_form = checkOutForm(request.POST)

        # This is driving me nuts. I get either
        #   error: form enter a whole number
        #   exception: must be a 'asset' instance
        # I can't satisfy both, so there's nothing I can do here,
        # and I can't find the underlying problem.

        # if log_form.is_valid():
        #     clean_log_form = log_form.cleaned_data

        #     asset_instance = asset.objects.get(assetID=clean_log_form["assetID"])
        #     log = OperationLog(
        #         assetID  = asset_instance,
        #         userID   = UserProfile.objects.get(id=request.user.id),
        #         location = clean_log_form["location"],
        #         notes    = clean_log_form["notes"]
        #     )
        #     log.save()

        #     prefix = asset_instance["assetPrefix"]
        #     return redirect(f"/assetManagement/{prefix}")
        messages.add_message(request, messages.SUCCESS, "Checkout Complete")
        return checkoutBandaid(request)

    # Not POST leads to index. Ought to be 404.
    return redirect("/")

def checkoutBandaid(request):
    """
    A function is specifically written to work with raw POST data, no validation.
    This function needs to be removed before final release as it is not sanitised.
    """

    asset_instance = asset.objects.get(assetID=request.POST["assetID"])
    log = OperationLog(
        assetID  = asset_instance,
        userID   = UserProfile.objects.get(id=request.user.id),
        location = request.POST["location"],
        notes    = request.POST["notes"]
    )
    log.save()

    prefix = asset_instance.assetPrefix

    return redirect(f"/asset/{prefix}")

@login_required(login_url="login")
def checkin(request):
    """
    Page showing the user's currently checked out assets and allowing them to check in.
    """

    if request.method == "GET":
        currently_checked_out = OperationLog.objects.filter(
            userID=request.user.id,
            endDateTime__isnull=True,
            deleted=False
        )

        # Making dictionary lists for the asset types.
        logs = {"SE": [], "LE": [], "LV": [], "HV": []}
        for log in currently_checked_out:
            prefix = log.assetID.assetPrefix
            logs[prefix].append({
                "logID"        : log.logID,
                "startDateTime": log.startDateTime,
                "location"     : log.location,
                "notes"        : log.notes,
                "assetName"    : log.assetID.assetName,
                "assetPrefix"  : log.assetID.assetPrefix,
                "assetID"      : log.assetID.assetID,
                "usageMinutes": log.usageMinutes,
                "usageHours": log.usageHours
            })

        assetLogs = [
            (logs[prefix], AssetStructures.assetLabelMapper[prefix])
            for prefix in ["SE", "LE", "LV", "HV"]
        ]

        for i in range(len(assetLogs) - 1, -1, -1):
            if len(assetLogs[i][0]) == 0:
                assetLogs.pop(i)

        previous_checked_out = OperationLog.objects.filter(
            userID=request.user.id,
            endDateTime__isnull=False,
            deleted=False
        )

        previous_logs = {"SE": [], "LE": [], "LV": [], "HV": []}
        for log in previous_checked_out:
            prefix = log.assetID.assetPrefix
            previous_logs[prefix].append({
                "logID"        : log.logID,
                "startDateTime": log.startDateTime,
                "endDateTime"  : log.endDateTime,
                "location"     : log.location,
                "notes"        : log.notes,
                "assetName"    : log.assetID.assetName,
                "assetPrefix"  : log.assetID.assetPrefix,
                "assetID"      : log.assetID.assetID,
                 "usageMinutes": log.usageMinutes,
                "usageHours": log.usageHours
            })

        previous_assetLogs = [
            (previous_logs[prefix], AssetStructures.assetLabelMapper[prefix])
            for prefix in ["SE", "LE", "LV", "HV"]
        ]

        for i in range(len(previous_assetLogs) - 1, -1, -1):
            if len(previous_assetLogs[i][0]) == 0:
                previous_assetLogs.pop(i)

        checkinForm = checkInForm()

        context = {
            "assetLogs"   : assetLogs,
            "previousLogs": previous_assetLogs,
            "checkinForm" : checkinForm
        }

        return render(request, "assetOperation/userAssets.html", context)

    if request.method == "POST":
        log_form = checkInForm(request.POST)

        if log_form.is_valid():
            clean_log_form = log_form.cleaned_data

            # Get the corresponding log and asset
            log = OperationLog.objects.get(logID=clean_log_form["logID"])
            asset = log.assetID  # Get the asset associated with the log
            farm = request.user.farm_id
            # email = farm.

            # Increment the usageMinutes of the asset
            usage_increment = clean_log_form.get("usage", 0)  # Get usage from the form
            asset.usageMinutes += usage_increment  # Increment asset usage
            asset.save()  # Save changes to the asset
            parts = asset.parts.all()
            print(parts)
            for part in parts:
                print('Test ', part.hours_before_maintenance, " Test2 ", asset.usageMinutes)
                if asset.usageMinutes >= (part.hours_before_maintenance*60):
                    print('Test ', part.hours_before_maintenance, " Test2 ", asset.usageMinutes)
                    subject = f"Maintenance Required for {asset.assetName}"
                    message = f"Maintenance Required for {asset.assetName}"
                    send_notification_email(subject, message, request.user.email)
            # Update log details
            log.endDateTime = datetime.now()
            log.notes = clean_log_form["notes"]
            log.usageMinutes = clean_log_form["usage_minutes"]
            log.usageHours = clean_log_form["usage_hours"]
            log.save()

            messages.add_message(request, messages.SUCCESS, "Check in Complete")

    return redirect("/operations/myCheckouts")


from django.core.mail import send_mail

def send_notification_email(subject, message, recipient_email):
    recipient_list = [recipient_email]
    send_mail(
        subject,                 # Email subject
        message,                 # Email message body
        'mathewkarunaratne@gmail.com',  # From email
        recipient_list,          # List of recipients
        fail_silently=False,     # If False, raises exceptions in case of failure
    )

# Logs on specific asset
@login_required(login_url="login")
def viewLogs(request, assetCategory, assetID):
    """
    Page showing all operation logs for the current asset.
    """

    if request.method == "GET":
        logs = OperationLog.objects.filter(
            assetID=asset.objects.get(assetID=assetID),
            deleted=False
        )

        asset_instance = asset.objects.get(assetID=assetID)

        # Bodge to make the notes and username work
        logs_dict = logs.values()
        for i, log in enumerate(logs_dict):
            if len(log["notes"]) < MAX_NOTES_HEAD:
                notesHead = log["notes"]
            else:
                notesHead = log["notes"][:MAX_NOTES_HEAD] + "..."
            logs_dict[i]["notesHead"] = notesHead
            logs_dict[i]["userName"] = logs[i].userID.username

        context = {
            "logs"        : logs_dict,
            "assetName"   : asset_instance.assetName,
            "currentAsset": asset_instance,
            "assetID"     : assetID,
            "assetPrefix" : asset_instance.assetPrefix,
        }

        return render(request, "assetOperation/assetLogs.html", context)


# Logs for all checkouts
@login_required(login_url="login")
def allCheckouts(request):
    if request.method == "GET":
        currently_checked_out = OperationLog.objects.filter(
            endDateTime__isnull=True,
            deleted=False
        )

        # Making dictionary lists for the asset types.
        # SQL join would make this so much more efficient.
        logs = {"SE": [], "LE": [], "LV": [], "HV": []}
        for log in currently_checked_out:
            prefix = log.assetID.assetPrefix
            # Everything we want on the client side
            if len(log.notes) < MAX_NOTES_HEAD:
                notesHead = log.notes
            else:
                notesHead = log.notes[:MAX_NOTES_HEAD] + "..."
            logs[prefix].append({
                "logID"        : log.logID,
                "startDateTime": log.startDateTime,
                "location"     : log.location,
                "notes"        : log.notes,
                "notesHead"    : notesHead,

                "userName"     : log.userID.username,

                "assetName"    : log.assetID.assetName,
                "assetPrefix"  : log.assetID.assetPrefix,
                "assetID"      : log.assetID.assetID
            })

        # List of tuples of (logs for type of asset, label for type of asset)
        assetLogs = [
            (logs[prefix], prefix)
            for prefix in ["SE", "LE", "LV", "HV"]
        ]

        context = {
            "assetLogs": assetLogs
        }

        return render(request, "assetOperation/allCheckouts.html", context)
