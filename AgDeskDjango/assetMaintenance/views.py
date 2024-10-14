from django.shortcuts import render, redirect
from . import forms
from .models import Maintenance, Damage
from . import models
from assetManagement.models import asset, SmallEquipment, LargeEquipment, lightVehicle, heavyVehicle
from assetManagement.views import AssetManager, AssetStructures
from django.core import serializers
from django.contrib import messages
from django.http import JsonResponse
from django.forms.models import model_to_dict

# Create your views here.

class maintenanceManager():
    """
    Queries the Maintenance Model and returns maintenance records for assets.

    Arguments:

        assetID: int
        The ID of the asset to retrieve maintenance data for, if this is left blank all assets of a provided class will be retrieved.

        assetCategory: str
        The category of asset to retrieve maintenance data for, if this is left blank all maintenance records in the database will be retrieved.
    """

    def retrieveMaintenanceData(self, assetID = None, assetCategory = "ALL"):
        if assetID is not None and assetCategory != "ALL":
            #assetID_assetPrefix is a foreign key, so we can use the __ notation to access the assetPrefix field. Review Function documentation below.
            """
            field_name
            The name of the model field that is filtered against. 
            If this argument is not provided, it defaults the filter's attribute name on the FilterSet class. 
            Field names can traverse relationships by joining the related parts with the ORM lookup separator (__). e.g., a product's manufacturer__name.
            """
            recordsFound = Maintenance.objects.filter(assetID = assetID, assetID__assetPrefix = assetCategory, deleted = False)
            return recordsFound

        elif assetID is not None and assetCategory == "ALL":
            completeRecordSet = Maintenance.objects.filter(assetID = assetID, deleteed = False)
            return completeRecordSet

        elif assetID is None and assetCategory != "ALL":
            completeRecordSet = Maintenance.objects.filter(assetID__assetPrefix = assetCategory, deleted = False)
            return completeRecordSet

        else:
            completeRecordSet = Maintenance.objects.all(deleted=False)
            return completeRecordSet

    def createMaintenanceRecord(self, maintenanceData, assetCategory, assetID):
        """
        Runs a Creation Query on the Maintenance Model to create a new maintenance record.

        Arguments:

                maintenanceData: dict
                The data to create the maintenance record with, this should be in the form of a dictionary with the key being the field to update and the value being the new data.
                maintenanceData should be passed through in the following format:
                {
                    "assetID": int,
                    "assetCategory": str,
                    "completionDate": date,
                    "maintenanceType": int,
                    "maintenanceConductedBy": str,
                    "maintenanceLocation": str,
                    "maintenanceTasksCompleted": str,
                    "repairsCompleted": int,
                    "Cost": decimal,
                    "Notes": str,
                    "kmsBeforeNextService": int,
                    "dateOfNextService": date
                }
        """

        assetStructures = AssetStructures()
        targetAsset = assetStructures.assetModelMapper.get(assetCategory).objects.get(assetID = assetID)
        newRecord = Maintenance(assetID = targetAsset, 
                                completionDate = maintenanceData["completionDate"], 
                                maintenaceType = maintenanceData["maintenanceType"], 
                                maintenanceConductedBy = maintenanceData["maintenanceConductedBy"], 
                                maintenanceLocation = maintenanceData["maintenanceLocation"], 
                                maintenanceTasksCompleted = maintenanceData["maintenanceTasksCompleted"], 
                                repairsCompleted = maintenanceData["repairsCompleted"], 
                                Cost = maintenanceData["Cost"], 
                                Notes = maintenanceData["Notes"], 
                                kmsBeforeNextService = maintenanceData["kmsBeforeNextService"], 
                                dateOfNextService = maintenanceData["dateOfNextService"])
        newRecord.save()

    def editMaintenanceData(self, maintenanceLogID, updateData):
        """
        Queries the Maintenance Model and performs updates based on the provided arguments.

        Arguments:
            MaintenanceLogID: int
            the unique identifier for the maintenance Log you want to update

            updateData: dict
            The data to update the maintenance record with, this should be in the form of a dictionary with the key being the field to update and the value being the new data.
            update data should be passed in the following format:
            {
                "completionDate": date,
                "maintenanceType": int,
                "maintenanceConductedBy": str,
                "maintenanceLocation": str,
                "maintenanceTasksCompleted": str,
                "repairsCompleted": int,
                "Cost": decimal,
                "Notes": str,
                "kmsBeforeNextService": int,
                "dateOfNextService": date
            }
            NOTE: The assetID field cannot be updated, as this is a foreign key and should not be changed.
        """
        print(maintenanceLogID)
        targetMaintenanceRecord = Maintenance.objects.get(maintenanceID = maintenanceLogID)

        for key, value in updateData.items():
            setattr(targetMaintenanceRecord, key, value)
        targetMaintenanceRecord.save()

    def deleteMaintenanceData(self, maintenanceLogID):
        targetMaintenanceRecord = Maintenance.objects.get(maintenanceID = maintenanceLogID)
        targetMaintenanceRecord.deleted = True
        targetMaintenanceRecord.save()

    def retrieveMaintenanceRecordByID(self, maintenanceLogID):
        try:
            completeRecord = Maintenance.objects.get(pk=maintenanceLogID)
            completeRecord = model_to_dict(completeRecord)
            # Convert the date and times to user readable format from a datetime object
            completeRecord['completionDate'] = completeRecord['completionDate'].strftime("%d/%m/%Y")
            completeRecord['dateOfNextService'] = completeRecord['dateOfNextService'].strftime("%d/%m/%Y")
            return completeRecord
        except Damage.DoesNotExist:
            print("Maintenance Record Not Found")
            return {"error": "Maintenance Record Not Found"}
        except Exception as e:
            print(e)
            return {"error": str(e)}


class damageManager():
    def retrieveDamageData(self, assetID = None, assetCategory = "ALL"):
        #The unfiltered Queryset is stored in a variable to be used later.
        completeRecordSet = None
        #The query set after filtered to remove damage logs that are deleted or marked repaired.
        filteredRecordSet = []

        if assetID is not None and assetCategory != "ALL":
            completeRecordSet = Damage.objects.filter(assetID = assetID, assetID__assetPrefix = assetCategory, deleted = False)
            for damage in completeRecordSet:
                if (not self.checkDamageRepairedByID(damage.damageID)):
                    filteredRecordSet.append(damage)
                    print(damage)

        elif assetID is not None and assetCategory == "ALL":
            completeRecordSet = Damage.objects.filter(assetID = assetID, deleteed = False)
            for damage in completeRecordSet:
                if (not self.checkDamageRepairedByID(damage.damageID)):
                    filteredRecordSet.append(damage)
                    print(damage)

        elif assetID is None and assetCategory != "ALL":
            completeRecordSet = Damage.objects.filter(assetID__assetPrefix = assetCategory, deleted = False)
            for damage in completeRecordSet:
                if (not self.checkDamageRepairedByID(damage.damageID)):
                    filteredRecordSet.append(damage)
                    print(damage)

        else:
            completeRecordSet = Damage.objects.all(deleted=False)

        return filteredRecordSet

    def retrieveDamageRecordByID(self, damageLogID):
        try:
            completeRecord = Damage.objects.get(pk=damageLogID).__dict__
            completeRecord["damageObservedDate"] = completeRecord["damageObservedDate"].strftime("%d/%m/%Y")
            completeRecord["damageOccuredDate"] = completeRecord["damageOccuredDate"].strftime("%d/%m/%Y")
            completeRecord["scheduledMaintenanceDate"] = completeRecord["scheduledMaintenanceDate"].strftime("%d/%m/%Y")
            return completeRecord
        except Damage.DoesNotExist:
            print("Damage Record Not Found")
            return {"error": "Damage Record Not Found"}
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def createDamageRecord(self, damageData, assetCategory, assetID):
        assetStructures = AssetStructures()
        targetAsset = assetStructures.assetModelMapper.get(assetCategory).objects.get(assetID = assetID)

        newRecord = Damage(
            assetID = targetAsset,
            damageObservedDate = damageData["damageObservedDate"],
            damageOccuredDate = damageData["damageOccuredDate"],
            damageType = damageData["damageType"],
            damageSeverity = damageData["damageSeverity"],
            notes = damageData["notes"],
            damageImage = damageData["damageImage"],
            scheduledMaintenanceDate = damageData["scheduledMaintenanceDate"]
        )

        newRecord.save()

    def editDamageRecord(self, damageData, damageLogID):
        targetDamageRecord = Damage.objects.get(damageID = damageLogID)
        for key, value in damageData.items():
            setattr(targetDamageRecord, key, value)
        targetDamageRecord.save()

    def deleteDamageRecord(self, damageLogID):
        targetDamageRecord = Damage.objects.get(damageID = damageLogID)
        if targetDamageRecord.deleted != True:
            targetDamageRecord.deleted = True
            targetDamageRecord.save()

    # Check if damage on an asset has been repaired.    
    def checkDamageRepairedByID(self, MaintenanceID):
        return Maintenance.objects.filter(repairsCompleted=MaintenanceID).exists()


def retrieveDamageRecordByID(request, damageLogID):
    """
    Searches the Asset damage model based on a damage log ID provided as a parameter.

    Django Object Serialisation information obtained from documentation at: https://docs.djangoproject.com/en/5.0/topics/serialization/
        Django's serialization framework provides a mechanism for “translating” Django models into other formats.
        Usually these other formats will be text-based and used for sending Django data over a wire, 
        but it's possible for a serializer to handle any format.
        This function calls the serialiser object directly. This enables the image form data to be passed to the front end and autofilled.
    """

    try:
        completeRecord = Damage.objects.get(pk=damageLogID)
        data = model_to_dict(completeRecord)
        if completeRecord.damageImage:
            data["damageImage"] = completeRecord.damageImage.url
        print(data["damageImage"])
        return JsonResponse(data)
    except Damage.DoesNotExist:
        print("Damage Record Not Found")
        return JsonResponse({"error": "Damage Record Not Found"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)})


def get_maintenance_details(request, maintenance_id):
    # maintenance = Maintenance.objects.get(pk=maintenance_id)
    maintenanceManagerInstance = maintenanceManager()
    maintenance = maintenanceManagerInstance.retrieveMaintenanceRecordByID(maintenance_id)
    data = model_to_dict(maintenance)  # Converts the model instance to a dictionary
    data['completionDate'] = data['completionDate'].strftime("%d/%m/%Y")
    data['dateOfNextService'] = data['dateOfNextService'].strftime("%d/%m/%Y")
    return JsonResponse(data)


def viewMaintenance(request, assetCategory, assetID):
    maintenanceManagerInstance = maintenanceManager()
    assetManagerInstance = AssetManager()
    currentAsset = assetManagerInstance.retrieveAssetByID(assetCategory=assetCategory, currentUser=request.user, assetID=assetID)

    creationForm = forms.createMaintenanceForm(request.user, assetCategory, assetID)
    requestCreationForm = forms.requestMaintenance(request.user, assetCategory, assetID)
    editForm = forms.editMaintenanceForm(request.user, assetCategory, assetID)

    assetLabelMapper = {
        "SE": "Small Equipment",
        "LE": "Large Equipment",
        "LV": "Standard Vehicles",
        "HV": "Heavy Vehicles"
    } 

    if request.method == "GET":
        maintenanceData = maintenanceManagerInstance.retrieveMaintenanceData(assetID, assetCategory)
        context = {
            "currentAsset": currentAsset,
            "maintenanceData": maintenanceData,
            "assetCategory": assetCategory,
            "creationForm": creationForm,
            "requestCreationForm": requestCreationForm,
            "editForm": editForm,
            "assetLabel": assetLabelMapper[assetCategory]
        }
        return render(request, "assetMaintenance/viewMaintenance.html", context)

    elif request.method == "POST":
        print(request.POST)
        if "createMaintenance" in request.POST:
            creationFormPost = forms.createMaintenanceForm(request.user, assetCategory, assetID, request.POST)
            print("createMaintenance")
            if creationFormPost.is_valid():
                print("Form is valid")
                maintenanceManagerInstance.createMaintenanceRecord(creationFormPost.cleaned_data, assetCategory, assetID)
                maintenanceData = maintenanceManagerInstance.retrieveMaintenanceData(assetID, assetCategory)
                context = {
                    "maintenanceData": maintenanceData,
                    "assetCategory": assetCategory,
                    "maintenanceForm": creationFormPost,
                    "assetLabel": assetLabelMapper[assetCategory]
                }
                messages.add_message(request, messages.SUCCESS, "Maintenance Record Added")
            else:
                print(creationFormPost.errors)
        elif "requestMaintenance" in request.POST:
            requestFormPost = forms.requestMaintenance(request.user, assetCategory, assetID, request.POST)
            print("requestMaintenance")
            if requestFormPost.is_valid():
                print("Request Form is valid")
                # Process the request maintenance form, e.g., save it
                maintenanceManagerInstance.createMaintenanceRequest(requestFormPost.cleaned_data, assetCategory, assetID)
                messages.add_message(request, messages.SUCCESS, "Maintenance Request Submitted")
                return redirect(f'/asset/{assetCategory}/{assetID}/maintenance')  # Redirect after processing the request
            else:
                print(requestFormPost.errors)

            return redirect(f'/asset/{assetCategory}/{assetID}/maintenance') 

        elif "editMaintenance" in request.POST:
            print("Edit Maintenance")
            print(request.POST)
            editMaintenanceFormPost = forms.editMaintenanceForm(request.user, assetCategory, assetID, request.POST)
            if editMaintenanceFormPost.is_valid():
                print("Form is valid")
                maintenanceID = request.POST.get("maintenanceID")
                maintenanceManagerInstance.editMaintenanceData(maintenanceID, editMaintenanceFormPost.cleaned_data)
                maintenanceData = maintenanceManagerInstance.retrieveMaintenanceData(assetID, assetCategory)
                context = {
                    "maintenanceData": maintenanceData,
                    "assetCategory": assetCategory,
                    "maintenanceForm": editMaintenanceFormPost,
                    "assetLabel": assetLabelMapper[assetCategory]
                }
            else:
                print(editMaintenanceFormPost.errors)

        return redirect(f'/asset/{assetCategory}/{assetID}/maintenance')

    return render(request, "assetMaintenance/viewMaintenance.html", context)


def maintenanceDetails(request, assetCategory, assetID, maintenanceID):
    maintenanceManagerInstance = maintenanceManager()
    assetStrucutures = AssetStructures()
    maintenanceRecord = maintenanceManagerInstance.retrieveMaintenanceRecordByID(maintenanceID)
    # maintenanceRecord = model_to_dict(maintenanceRecord)
    currentAsset = assetStrucutures.assetModelMapper.get(assetCategory).objects.get(assetID = assetID)
    print(maintenanceID)
    form = forms.editMaintenanceForm(initial = maintenanceRecord)

    if request.method == "GET":
        context = {
            "currentAsset": currentAsset,
            "maintenanceRecord": maintenanceRecord,
            "assetCategory": assetCategory,
            "form": form
        }

        return render(request, "assetMaintenance/maintenanceDetails.html", context)

    elif request.method == "POST":
        if  "Update" in request.POST:
            formPOST = forms.editMaintenanceForm(request.user, assetCategory, assetID, request.POST, request.FILES)
            if formPOST.is_valid():
                maintenanceManagerInstance.editMaintenanceData(maintenanceID, formPOST.cleaned_data)
            else:
                print(formPOST.errors)

            return redirect(f'/asset/{assetCategory}/{assetID}/maintenance')

        elif "delete" in request.POST:
            maintenanceManagerInstance.deleteMaintenanceData(maintenanceID)

            return redirect(f'/asset/{assetCategory}/{assetID}/maintenance')

    return render(request, 'assetMaintenance/maintenanceDetails.html', context)


def deleteMaintenance(request, maintenanceID, assetCategory, assetID):
    maintenanceManagerInstance = maintenanceManager()
    maintenanceManagerInstance.deleteMaintenanceData(maintenanceID)
    messages.add_message(request, messages.WARNING, "Maintenance Record Deleted")

    return redirect(f'/asset/{assetCategory}/{assetID}/maintenance')


def viewDamage(request, assetCategory, assetID):
    damageManagerInstance = damageManager()
    assetStrucutures = AssetStructures()

    currentAsset = assetStrucutures.assetModelMapper.get(assetCategory).objects.get(assetID = assetID)
    creationForm = forms.createDamageForm(request.user, assetCategory, assetID)
    editForm = forms.editDamageForm(request.user, assetCategory, assetID)

    if request.method == "GET":
        damageData = damageManagerInstance.retrieveDamageData(assetID, assetCategory)
        context = {
            "currentAsset": currentAsset,
            "damageData": damageData,
            "assetCategory": assetCategory,
            "editForm": editForm,
            "creationForm": creationForm
        }

        return render(request, "assetMaintenance/viewDamage.html", context)
    
    elif request.method == "POST":
        creationFormPOST = forms.createDamageForm(request.user, assetCategory, assetID, request.POST, request.FILES)
        if creationFormPOST.is_valid():
            damageManagerInstance.createDamageRecord(creationFormPOST.cleaned_data, assetCategory, assetID)
            damageData = damageManagerInstance.retrieveDamageData(assetID, assetCategory)
            context = {
                "currentAsset": currentAsset,
                "damageData": damageData,
                "assetCategory": assetCategory,
                "creationForm": creationFormPOST
            }
            messages.add_message(request, messages.SUCCESS, "Damage Record Added")
        else:
            print(creationFormPOST.errors)

        return redirect(f'/asset/{assetCategory}/{assetID}/damage')

    return render(request, "assetMaintenance/viewDamage.html", context)


def damageDetails(request, assetCategory, assetID, damageID):
    damageManagerInstance = damageManager()
    assetStrucutures = AssetStructures()
    damageRecord = damageManagerInstance.retrieveDamageRecordByID(damageID)
    currentAsset = assetStrucutures.assetModelMapper.get(assetCategory).objects.get(assetID = assetID)
    form = forms.editDamageForm(initial = damageRecord)
    print(damageRecord)

    if request.method == "GET":
        context = {
            "currentAsset": currentAsset,
            "damageRecord": damageRecord,
            "assetCategory": assetCategory,
            "form": form
        }

        return render(request, "assetMaintenance/damageDetails.html", context)

    elif request.method == "POST":
        if  "Update" in request.POST:
            formPOST = forms.editDamageForm(request.user, assetCategory, assetID, request.POST, request.FILES)
            if formPOST.is_valid():
                damageManagerInstance.editDamageRecord(formPOST.cleaned_data, damageID)
            else:
                print(formPOST.errors)

            return redirect(f'/asset/{assetCategory}/{assetID}/damage')

        elif "delete" in request.POST:
            damageManagerInstance.deleteDamageRecord(damageID)

            return redirect(f'/asset/{assetCategory}/{assetID}/damage')

    return render(request, 'assetMaintenance/damageDetails.html', context)


def deleteDamage(request, damageID, assetCategory, assetID):
    damageManagerInstance = damageManager()
    damageManagerInstance.deleteDamageRecord(damageID)
    messages.add_message(request, messages.WARNING, "Damage Record Deleted")

    return redirect(f'/asset/{assetCategory}/{assetID}/damage')
