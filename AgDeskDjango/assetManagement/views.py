import datetime
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from .models import SmallEquipment, LargeEquipment, lightVehicle, heavyVehicle, AssetPart
from . import forms
from UserAuth.models import UserProfile
from FarmAcc.models import FarmInfo
from assetOperation.models import OperationLog
from assetOperation.forms import checkOutForm
from assetManagement.forms import AssetPartFormSet
from itertools import chain
from django.contrib import messages


class AssetStructures():

    assetLabelMapper = {
        "SE": "Small Equipment",
        "LE": "Large Equipment",
        "LV": "Standard Vehicles",
        "HV": "Heavy Vehicles"
    }

    assetModelMapper = {
        "SE": SmallEquipment,
        "LE": LargeEquipment,
        "LV": lightVehicle,
        "HV": heavyVehicle
    }

    assetCreationFormMapper = {
        "SE": forms.createSmallAssetForm,
        "LE": forms.createLargeAssetForm,
        "LV": forms.createLightVehicleForm,
        "HV": forms.createHeavyVehicleForm
    }

    assetEditFormMapper = {
        "SE": forms.editSmallAssetForm,
        "LE": forms.editLargeAssetForm,
        "LV": forms.editLightVehicleForm,
        "HV": forms.editHeavyVehicleForm
    }

    # Used to generate asset forms when they are part of a POST request.
    def generatePOSTForm(self, assetClass, request, postRequest = None, additionalrequest = None, formType = "create", ):
        if formType == "create":
            return AssetStructures.assetCreationFormMapper.get(assetClass)(request, postRequest , additionalrequest)
        elif formType == "edit":
            return AssetStructures.assetEditFormMapper    .get(assetClass)(request, postRequest , additionalrequest)
        else:
            raise Exception("Invalid formType")

# I'm not sure where this docstring belongs, or if it even is a docstring.
"""
- Asset Category should be passed in via the URL as one of the following.
    - SE
    - LE
    - SV
    - HV
    - ALL
Capitalisation is not relevant. This is handled in the below method.
"""

# If the uncommented code is not working, try the commented code.
# Uncommented code has not been tested yet
class AssetManager():

    def retrieveAssets(self, assetCategory, currentUser):
        """
        This function will indiscriminately return all assets of a given type from the farm
        type = Large or Small Equipment & Heavy or standard Vehicles.
        """

        currentFarmID = currentUser.currentFarm_id
        assetStructures = AssetStructures()
        queryCategory = None
        for key, value in assetStructures.assetModelMapper.items():
            if key == assetCategory:
                queryCategory = value.objects.filter(farmID = currentFarmID, deleted = 0).values()

        if assetCategory == "all":
            #Query for all assets
            allAssetsQuerySet = chain(
                SmallEquipment.objects.filter(farmID = currentFarmID).values(), 
                LargeEquipment.objects.filter(farmID = currentFarmID).values(), 
                lightVehicle  .objects.filter(farmID = currentFarmID).values(), 
                heavyVehicle  .objects.filter(farmID = currentFarmID).values()
            )

            return allAssetsQuerySet
        else:
            return queryCategory

    def retrieveAssetByID(self, assetCategory, currentUser, assetID):
        assetStructures = AssetStructures()
        currentFarmID = currentUser.currentFarm_id
        assetValues = assetStructures.assetModelMapper.get(assetCategory).objects.get(farmID=currentFarmID, assetID=assetID).__dict__
        assetValues["datePurchased"] = assetValues["datePurchased"].strftime("%d/%m/%Y")
        assetValues["dateManufactured"] = assetValues["dateManufactured"].strftime("%d/%m/%Y")

        return assetValues

    def createAsset(self, assetCategory, assetData):
        farmQuery = FarmInfo.objects.filter(id=assetData["farmID"])

        if assetCategory == "SE":
            newSmallEquipment = SmallEquipment(
                assetPrefix      = "SE",
                assetName        = assetData["formData"]["assetName"],
                farmID           = farmQuery[0],
                dateManufactured = assetData["formData"]['dateManufactured'],
                datePurchased    = assetData["formData"]['datePurchased'],
                vin     = assetData["formData"]["vin"],
                Manufacturer     = assetData["formData"]["Manufacturer"],
                Location         = assetData["formData"]["Location"],
                assetImage       = assetData["formData"]["assetImage"]
            )
            newSmallEquipment.save()
            return newSmallEquipment
        elif assetCategory == "LE":
            newSmallEquipment = LargeEquipment(
                assetPrefix      = "LE",
                assetName        = assetData["formData"]["assetName"],
                farmID           = farmQuery[0],
                dateManufactured = assetData["formData"]['dateManufactured'],
                datePurchased    = assetData["formData"]['datePurchased'],
                vin     = assetData["formData"]["vin"],
                Manufacturer     = assetData["formData"]["Manufacturer"],
                Location         = assetData["formData"]["Location"],
                assetImage       = assetData["formData"]["assetImage"]
            )
            newSmallEquipment.save()
            return newSmallEquipment
        elif assetCategory == "LV":
            newSmallEquipment = lightVehicle(
                assetPrefix      = "LV",
                assetName        = assetData["formData"]["assetName"],
                farmID           = farmQuery[0],
                dateManufactured = assetData["formData"]['dateManufactured'],
                datePurchased    = assetData["formData"]['datePurchased'],
                vin     = assetData["formData"]["vin"],
                Manufacturer     = assetData["formData"]["Manufacturer"],
                Location         = assetData["formData"]["Location"],
                assetImage       = assetData["formData"]["assetImage"]
            )
            newSmallEquipment.save()
            return newSmallEquipment
        elif assetCategory == "HV":
            newSmallEquipment = heavyVehicle(
                assetPrefix      = "HV",
                assetName        = assetData["formData"]["assetName"],
                farmID           = farmQuery[0],
                dateManufactured = assetData["formData"]['dateManufactured'],
                datePurchased    = assetData["formData"]['datePurchased'],
                vin     = assetData["formData"]["vin"],
                Manufacturer     = assetData["formData"]["Manufacturer"],
                Location         = assetData["formData"]["Location"],
                assetImage       = assetData["formData"]["assetImage"]
            )
            newSmallEquipment.save()
            return newSmallEquipment



    # Handle other asset categories similarly...


    def editAsset(self, assetCategory,  assetData, assetID):
        assetStructures = AssetStructures()
        targetAsset = assetStructures.assetModelMapper.get(assetCategory).objects.get(assetID=assetID)

        if assetData["assetImage"] == None:
            assetData["assetImage"] = "images/asset_images/defaultImage.jpg"

        if assetCategory == "SE":
            #Edit a small equipment object
            targetAsset.assetName        = assetData["assetName"       ]
            targetAsset.dateManufactured = assetData["dateManufactured"]
            targetAsset.datePurchased    = assetData["datePurchased"   ]
            targetAsset.vin     = assetData["vin"    ]
            targetAsset.Manufacturer     = assetData["Manufacturer"    ]
            # targetAsset.partsList        = assetData["partsList"       ]
            targetAsset.Location         = assetData["Location"        ]
            targetAsset.assetImage       = assetData["assetImage"      ]

        elif assetCategory == "LE":
            #update target asset fields.
            targetAsset.assetName     = assetData["assetName"    ]
            targetAsset.datePurchased = assetData["datePurchased"]
            targetAsset.vin           = assetData["vin"          ]
            targetAsset.Manufacturer  = assetData["Manufacturer" ]
            # targetAsset.partsList     = assetData["partsList"    ]
            targetAsset.Location      = assetData["Location"     ]
            targetAsset.assetImage    = assetData["assetImage"   ]

        elif assetCategory == "LV":
            #update target asset fields.
            targetAsset.assetName      = assetData["assetName"     ]
            targetAsset.datePurchased  = assetData["datePurchased" ]
            targetAsset.vin            = assetData["vin"           ]
            targetAsset.Manufacturer   = assetData["Manufacturer"  ]
            # targetAsset.partsList      = assetData["partsList"     ]
            targetAsset.Location       = assetData["Location"      ]
            targetAsset.Registration   = assetData["Registration"  ]
            targetAsset.currentlyInUse = assetData["currentlyInUse"]
            targetAsset.assetImage     = assetData["assetImage"    ]

        elif assetCategory == "HV":
            #update target asset fields.
            targetAsset.assetName          = assetData["assetName"         ]
            targetAsset.datePurchased      = assetData["datePurchased"     ]
            targetAsset.vin                = assetData["vin"               ]
            targetAsset.Manufacturer       = assetData["Manufacturer"      ]
            # targetAsset.partsList          = assetData["partsList"         ]
            targetAsset.Location           = assetData["Location"          ]
            targetAsset.Registration       = assetData["Registration"      ]
            targetAsset.inTransport        = assetData["inTransport"       ]
            targetAsset.interFarmTransport = assetData["interFarmTransport"]
            targetAsset.assetImage         = assetData["assetImage"        ]

        targetAsset.save()

    def deleteAsset(self, assetID, assetCategory):
        """
        Soft deletes a task from the database by setting the deleted field to True.
        """

        assetStructures = AssetStructures()
        targetAsset = assetStructures.assetModelMapper.get(assetCategory).objects.get(assetID=assetID)

        try:
            targetAsset.deleted = True
            targetAsset.save()

            return {"deletionStatus": "Success"}
        except:
            return {"deletionStatus": "Failed, Asset already deleted."}

    def calculateAssetAge(self, assetClass, assetID):
        """
        This function will calculate the age of an asset based on the date of manufacture or  purchase.
        """

        assetStructures = AssetStructures()
        target = assetStructures.assetModelMapper.get(assetClass).objects.get(assetID=assetID)
        currentDate = datetime.date.today()

        if target.dateManufactured is not None:
            age = currentDate - target.dateManufactured
        #else block is for assets where the date of manufacture is unkown
        else:
            age = currentDate - target.datePurchased

        return age


# View functions
from django.forms import inlineformset_factory
from django.http import HttpResponse

def displayAssets(request, assetCategory):
    assetManager = AssetManager()
    assetStructures = AssetStructures()
    currentUser = UserProfile.objects.get(id=request.user.id)

    ### Get Request ###
    if request.method == "GET":
        creationForm = assetStructures.assetCreationFormMapper.get(assetCategory)(request.user)
        partFormSet = AssetPartFormSet(queryset=AssetPart.objects.none())  # No initial parts

        assets = assetManager.retrieveAssets(assetCategory, currentUser)
        for asset in assets:
            for key, value in asset.items():
                if key == "dateManufactured" or key == "datePurchased":
                    assetManager.calculateAssetAge(assetCategory, asset["assetID"])

            # True if being used, False if NOT being used
            lastLog = OperationLog.objects.filter(assetID=asset["assetID"], endDateTime__isnull=True)
            asset["opStatus"] = len(lastLog) > 0

        checkoutForm = checkOutForm()

        context = {
            'assetList'    : assets,
            'assetCategory': assetCategory,
            'assetForm'    : creationForm,
            'assetLabel'   : assetStructures.assetLabelMapper.get(assetCategory),
            'checkoutForm' : checkoutForm,
            'partFormSet'  : partFormSet,  # Add the formset for asset parts
        }

        return render(request, 'assetManagement/assetOverview.html', context)

    ### Post Request ###
    elif request.method == "POST":
        creationForm = assetStructures.generatePOSTForm(assetCategory, request.user, request.POST, request.FILES, "create")
        partFormSet = AssetPartFormSet(request.POST)  # Bind the part formset with the POST data

        if creationForm.is_valid() and partFormSet.is_valid():
            # Create the asset
            context = {
                "farmID": currentUser.currentFarm_id,
                "formData": creationForm.cleaned_data
            }
            
            # Save the asset and retrieve the instance
            new_asset = assetManager.createAsset(assetCategory, context)  # Ensure createAsset returns the asset instance
            print(new_asset)
            # Save the parts if any were submitted
            if partFormSet.cleaned_data:
                for part_form in partFormSet.cleaned_data:
                    if part_form and part_form.get('part_name') and part_form.get('hours_before_maintenance'):
                        AssetPart.objects.create(
                            asset=new_asset,  # Use the newly created asset instance
                            part_name=part_form['part_name'],
                            hours_before_maintenance=part_form['hours_before_maintenance']
                        )

            messages.add_message(request, messages.SUCCESS, "New Asset Created.")
            return redirect(f'/asset/{assetCategory}')
        else:
            # For debugging invalid form(s)
            print(creationForm.errors)
            print(partFormSet.errors)

        # If the form is invalid, re-render the page with the errors
        return render(request, 'assetManagement/assetOverview.html', {
            'assetForm': creationForm,
            'partFormSet': partFormSet,
            'assetCategory': assetCategory,
            'assetList': assetManager.retrieveAssets(assetCategory, currentUser),
            'checkoutForm': checkOutForm(),
        })





def createAsset(request):
    assetManager = AssetManager()
    currentUser = UserProfile.objects.get(id=request.user.id)


def viewAsset(request, assetCategory, assetID):
    assetManager = AssetManager()
    assetStructures = AssetStructures()
    currentUser = UserProfile.objects.get(id=request.user.id)
    asset = assetManager.retrieveAssetByID(assetCategory, currentUser, assetID)
    # Get the form for the asset type & set the initial values of the form to the asset values.
    form = assetStructures.assetEditFormMapper.get(assetCategory)(initial=asset)

    ### Get Request ###
    if request.method == "GET":
        context = {
            'currentAsset' : asset,
            'assetCategory': assetCategory,
            'assetForm'    : form,
            'assetLabel'   : assetStructures.assetLabelMapper.get(assetCategory)
        }

        return render(request, 'assetManagement/assetDetails.html', context)

    if request.method == "POST":
        form = assetStructures.generatePOSTForm(assetCategory, request.user, request.POST, request.FILES, "edit")

        # Edit Asset
        if "Update" in request.POST: 
            if form.is_valid():
                assetManager.editAsset(assetCategory, form.cleaned_data, assetID)
                messages.add_message(request, messages.SUCCESS, "Successfully saved.")
            else:
                print(form.errors)

            return redirect(f'/asset/{assetCategory}/{assetID}/details')

        # Delete Asset
        elif "delete" in request.POST: # Delete Asset
            assetManager.deleteAsset(assetID, assetCategory)
            messages.add_message(request, messages.WARNING, "Asset Deleted")

            return redirect(f'/asset/{assetCategory}')

        return redirect(f'/asset/{assetCategory}/{assetID}/details')

    return render(request, 'assetManagement/assetDetails.html')
