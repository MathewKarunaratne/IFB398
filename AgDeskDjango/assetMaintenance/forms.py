from datetime import datetime,date
from django import forms
from django.forms import ModelForm
from . import models
from .models import Maintenance, Damage
from FarmAcc.models import FarmInfo
from assetManagement.models import asset
from UserAuth.models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit,Row, Column, Div, HTML
from crispy_forms.bootstrap import Modal,StrictButton,PrependedText

def getUsersOnFarm(currUserFarmID):
    farmInstance = FarmInfo.objects.get(id = currUserFarmID)
    return farmInstance.userprofile_set.all()

def getDamageObjects(assetID, assetPrefix):
    return Damage.objects.filter(assetID = assetID, assetID__assetPrefix = assetPrefix, deleted = False)

class createMaintenanceForm(ModelForm):
    def __init__(self, user = None, assetCategory = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('maintenanceType','completionDate', 'repairsCompleted', 'maintenanceTasksCompleted', css_class='form-group col-md-6 mb-0'),
                Column('maintenanceConductedBy', 'maintenanceLocation', 'Cost', 'Notes', css_class='form-group col-md-6 mb-0')
            ),
            Row(HTML('<h4>Next Service Details</h4>')),
            Row( 
                Column('dateOfNextService',css_class='form-group col-md-6 mb-0'),
                Column('kmsBeforeNextService',css_class='form-group col-md-6 mb-0')
            ),
            StrictButton("Close", css_class="btn btn-secondary float-left", data_bs_dismiss="modal"),
            StrictButton("Add Maintenance", type="submit", name='createMaintenance',css_class="btn custom-button float-right")
        )

        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["completionDate"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceType"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceConductedBy"].queryset = getUsersOnFarm(currentFarmID)
            self.fields["maintenanceLocation"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceTasksCompleted"].widget.attrs.update({"class": "form-control"})
            self.fields["repairsCompleted"].queryset = getDamageObjects(assetID, assetCategory)
            self.fields["Cost"].widget.attrs.update({"class": "form-control"})
            self.fields["Notes"].widget.attrs.update({"class": "form-control"})
            self.fields["kmsBeforeNextService"].widget.attrs.update({"class": "form-control"})
            self.fields["dateOfNextService"].widget.attrs.update({"class": "form-control"})

    completionDate = forms.DateField(input_formats=["%d/%m/%Y"], label="Completion Date", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))
    maintenanceType = forms.ChoiceField(choices=models.maintenanceTypeChoices, label="Maintenance Type", widget=forms.Select(attrs={'class': 'form-control'}))
    maintenanceConductedBy = forms.ModelChoiceField(queryset = UserProfile.objects.all(), label="Maintenance Conducted By", widget=forms.Select(attrs={'class': 'form-control'}))
    maintenanceLocation = forms.CharField(label="Maintenance Location", widget=forms.TextInput(attrs={'class': 'form-control'}))
    maintenanceTasksCompleted = forms.CharField(label="Maintenance Tasks Completed", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    repairsCompleted = forms.ModelChoiceField(queryset = Damage.objects.all(), required=False, label="Repairs Completed", widget=forms.Select(attrs={'class': 'form-control'}))
    Cost = forms.DecimalField(label="Cost ($)", decimal_places = 2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    Notes = forms.CharField(label="Notes", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    kmsBeforeNextService = forms.IntegerField(label="Kms Before Next Service", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    dateOfNextService = forms.DateField(input_formats=["%d/%m/%Y"], label="Date Of Next Service", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))

    def clean(self):
        completionDate = self.cleaned_data.get("completionDate")
        dateOfNextService = self.cleaned_data.get("dateOfNextService")
        kmsBeforeNextService = self.cleaned_data.get("kmsBeforeNextService")
        cost = self.cleaned_data.get("Cost")
        errorMessages = []

        if completionDate > dateOfNextService:
            errorMessages.append('Completion date cannot be after the date of next service. ')
            self._errors["completionDate"] = self.error_class(["Completion date cannot be after the date of next service."])


        if completionDate > datetime.date(datetime.today()):
            errorMessages.append("CompletionDate cannot be in the future.")
            self._errors["completionDate"] = self.error_class(["CompletionDate cannot be in the future."])

        if kmsBeforeNextService < 0:
            errorMessages.append("Kilometres before next service cannot be a negative value")
            self._errors["kmsBeforeNextService"] = self.error_class(["Kilometres before next service cannot be a negative value"])

        if cost < 0:
            errorMessages.append("Cost cannot be a negative value")
            self._errors["Cost"] = self.error_class(["Cost cannot be a negative value"])

        if len(errorMessages):
            raise forms.ValidationError(' & '.join(errorMessages))

        return self.cleaned_data

    class Meta:
        model = Maintenance
        fields = [
            'completionDate',
            'maintenanceType',
            'maintenanceConductedBy',
            'maintenanceLocation',
            'maintenanceTasksCompleted',
            'repairsCompleted',
            'Cost',
            'Notes',
            'kmsBeforeNextService',
            'dateOfNextService'
        ]


class editMaintenanceForm(ModelForm):
    def __init__(self, user = None, assetCategory = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'maintenanceID',
            Row(
                Column('maintenanceType','completionDate', 'repairsCompleted', 'maintenanceTasksCompleted', css_class='form-group col-md-6 mb-0'),
                Column('maintenanceConductedBy', 'maintenanceLocation', 'Cost', 'Notes', css_class='form-group col-md-6 mb-0')
            ),
            Row(HTML('<h4>Next Service Details</h4>')),
            Row( 
                Column('dateOfNextService',css_class='form-group col-md-6 mb-0'),
                Column('kmsBeforeNextService',css_class='form-group col-md-6 mb-0')
            ),
            StrictButton("Update", type="submit",name='Update',css_class="btn custom-button"),
            StrictButton("Delete", type="submit", name='delete', css_class="btn btn-danger")
        )

        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["completionDate"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceType"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceConductedBy"].queryset = getUsersOnFarm(currentFarmID)
            self.fields["maintenanceLocation"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceTasksCompleted"].widget.attrs.update({"class": "form-control"})
            self.fields["repairsCompleted"].queryset = self.fields["repairsCompleted"].queryset = getDamageObjects(assetID, assetCategory)
            self.fields["Cost"].widget.attrs.update({"class": "form-control"})
            self.fields["Notes"].widget.attrs.update({"class": "form-control"})
            self.fields["kmsBeforeNextService"].widget.attrs.update({"class": "form-control"})
            self.fields["dateOfNextService"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceID"].widget.attrs.update({"class": "form-control"})

    completionDate = forms.DateField(input_formats=["%d/%m/%Y"], label="Completion Date", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'When service will be/was complete - DD/MM/YYYY'}))
    maintenanceType = forms.ChoiceField(choices=models.maintenanceTypeChoices, label="Maintenance Type", widget=forms.Select(attrs={'class': 'form-control'}))
    maintenanceConductedBy = forms.ModelChoiceField(queryset = UserProfile.objects.all(), label="Maintenance Conducted By", widget=forms.Select(attrs={'class': 'form-control'}))
    maintenanceLocation = forms.CharField(label="Maintenance Location", widget=forms.TextInput(attrs={'class': 'form-control'}))
    maintenanceTasksCompleted = forms.CharField(label="Maintenance Tasks Completed", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    repairsCompleted = forms.ModelChoiceField(queryset = Damage.objects.all(), required=False, label="Repairs Completed", widget=forms.Select(attrs={'class': 'form-control'}))
    Cost = forms.DecimalField(label="Cost ($)", decimal_places = 2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    Notes = forms.CharField(label="Notes", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    kmsBeforeNextService = forms.IntegerField(label="Kms Before Next Service", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    dateOfNextService = forms.DateField(input_formats=["%d/%m/%Y"], label="Date Of Next Service", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))
    maintenanceID = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Maintenance
        fields = [
            'completionDate',
            'maintenanceType',
            'maintenanceConductedBy',
            'maintenanceLocation',
            'maintenanceTasksCompleted',
            'repairsCompleted',
            'Cost',
            'Notes',
            'kmsBeforeNextService',
            'dateOfNextService',
            'maintenanceID'
        ]

class requestMaintenance(ModelForm):
    def __init__(self, user=None, assetCategory=None, assetID=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('maintenanceType', 'invoice', css_class='form-group col-md-6 mb-0'),
                Column('component', 'severity', css_class='form-group col-md-6 mb-0')
            ),
            Row(
                Column('dateOfMaintenance', 'Cost', css_class='form-group col-md-6 mb-0'),
                Column('maintenanceLocation', 'Notes', css_class='form-group col-md-6 mb-0')
            ),
            StrictButton("Close", css_class="btn btn-secondary float-left", data_bs_dismiss="modal"),
            StrictButton("Send Request", type="submit", name='sendMaintenanceRequest', css_class="btn custom-button float-right")
        )

        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username=user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["maintenanceType"].widget.attrs.update({"class": "form-control"})
            self.fields["component"].widget.attrs.update({"class": "form-control"})
            self.fields["severity"].widget.attrs.update({"class": "form-control"})
            self.fields["dateOfMaintenance"].widget.attrs.update({"class": "form-control"})
            self.fields["maintenanceLocation"].widget.attrs.update({"class": "form-control"})
            self.fields["Cost"].widget.attrs.update({"class": "form-control"})
            self.fields["Notes"].widget.attrs.update({"class": "form-control"})
            self.fields["invoice"].widget.attrs.update({"class": "form-control"})  # Update for invoice

    # Existing fields
    maintenanceType = forms.ChoiceField(choices=models.maintenanceTypeChoices, label="Maintenance Type", widget=forms.Select(attrs={'class': 'form-control'}))
    component = forms.CharField(label="Component", widget=forms.TextInput(attrs={'class': 'form-control'}))
    severity = forms.ChoiceField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], label="Severity", widget=forms.Select(attrs={'class': 'form-control'}))
    dateOfMaintenance = forms.DateField(input_formats=["%d/%m/%Y"], label="Date of Maintenance", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'DD/MM/YYYY'}))
    maintenanceLocation = forms.CharField(label="Maintenance Location", widget=forms.TextInput(attrs={'class': 'form-control'}))
    # repairsCompleted = forms.ModelChoiceField(queryset=Damage.objects.all(), required=False, label="Repairs Completed", widget=forms.Select(attrs={'class': 'form-control'}))
    Cost = forms.DecimalField(label="Cost ($)", decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    Notes = forms.CharField(label="Notes", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    
    # New field for attaching the invoice
    invoice = forms.FileField(label="Invoice", required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    def clean(self):
        cost = self.cleaned_data.get("Cost")
        invoice = self.cleaned_data.get("invoice")
        errorMessages = []

        if cost < 0:
            errorMessages.append("Cost cannot be a negative value")
            self._errors["Cost"] = self.error_class(["Cost cannot be a negative value"])

        if invoice and not invoice.name.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            errorMessages.append("Invoice must be a PDF or image file (JPG, JPEG, PNG)")
            self._errors["invoice"] = self.error_class(["Invoice must be a PDF or image file"])

        if len(errorMessages):
            raise forms.ValidationError(' & '.join(errorMessages))

        return self.cleaned_data

    class Meta:
        model = Maintenance
        fields = [
            'maintenanceType',
            'component',
            'severity',
            'dateOfMaintenance',
            'maintenanceLocation',
            # 'repairsCompleted',
            'Cost',
            'Notes',
            'invoice'  # Include invoice in fields
        ]



class createDamageForm(ModelForm):
    def __init__(self, user = None, assetCategory = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('damageType', 'damageOccuredDate', 'damageImage', css_class='form-group col-md-6 mb-0'),
                Column('damageSeverity','damageObservedDate', 'scheduledMaintenanceDate',css_class='form-group col-md-6 mb-0')
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-0')
            ),
            StrictButton("Close", data_bs_dismiss="modal", style = "float: left;", css_class="btn btn-secondary"),
            StrictButton("Add Damage", type="submit",name='createDamage',style = "float: right;",css_class="btn custom-button")       
        )

        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["damageType"].widget.attrs.update({"class": "form-control"})
            self.fields["damageSeverity"].widget.attrs.update({"class": "form-control"})
            self.fields["damageObservedDate"].widget.attrs.update({"class": "form-control"})
            self.fields["damageOccuredDate"].widget.attrs.update({"class": "form-control"})
            self.fields["notes"].widget.attrs.update({"class": "form-control"})
            self.fields["scheduledMaintenanceDate"].widget.attrs.update({"class": "form-control"})
            self.fields["damageImage"].widget.attrs.update({"class": "form-control"})

    damageType               = forms.CharField(label="Damage Type", widget=forms.TextInput(attrs={'class': 'form-control'}))
    damageSeverity           = forms.ChoiceField(choices=models.damageSeverityChoice, label="Damage Severity", widget=forms.Select(attrs={'class': 'form-control'}))
    damageObservedDate       = forms.DateField(input_formats=["%d/%m/%Y"], label="Damage Observed Date", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))
    damageOccuredDate        = forms.DateField(input_formats=["%d/%m/%Y"], label="Damage Occured Date", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))
    notes                    = forms.CharField(label="Notes", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    scheduledMaintenanceDate = forms.DateField(input_formats=["%d/%m/%Y"], label="Scheduled Maintenance Date", widget=forms.DateInput(attrs={'class': 'form-control is-invalid', 'placeholder': 'Format - DD/MM/YYYY'}))
    damageImage              = forms.ImageField(label="Damage Image", widget=forms.FileInput(attrs={'class': 'form-control'}), initial=r"images/asset_images/defaultImage.jpg")

    class Meta:
        model = Damage
        fields = [
            'damageType',
            'damageSeverity',
            'damageObservedDate',
            'damageOccuredDate',
            'notes',
            'scheduledMaintenanceDate',
            'damageImage',
        ]


class editDamageForm(ModelForm):
    def __init__(self, user = None, assetCategory = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('damageType', 'damageSeverity', 'damageObservedDate', 'damageOccuredDate','notes', css_class='form-group col-md-6 mb-0'),
                Column(css_class='form-group col-md-2 mb-0'),
                Column(
                    Div(HTML('<img src="{{ damageRecord.damageImage.url }}" style="width: 200px; height: 200px;">'), css_class='text-right'),
                    Div('damageImage', 'scheduledMaintenanceDate'),
                    css_class='form-group col-md-4 mb-0')
            ),  
            StrictButton("Update", type="submit",name='Update',css_class="btn custom-button"),
            StrictButton("Delete", type="submit", name='delete', css_class="btn btn-danger")
        )

        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["damageType"].widget.attrs.update({"class": "form-control"})
            self.fields["damageSeverity"].widget.attrs.update({"class": "form-control"})
            self.fields["damageObservedDate"].widget.attrs.update({"class": "form-control"})
            self.fields["damageOccuredDate"].widget.attrs.update({"class": "form-control"})
            self.fields["notes"].widget.attrs.update({"class": "form-control"})
            self.fields["scheduledMaintenanceDate"].widget.attrs.update({"class": "form-control"})
            self.fields["damageImage"].widget.attrs.update({"class": "form-control"})

    damageType               = forms.CharField(label="Damage Type", widget=forms.TextInput(attrs={'class': 'form-control'}))
    damageSeverity           = forms.ChoiceField(choices=models.damageSeverityChoice, label="Damage Severity", widget=forms.Select(attrs={'class': 'form-control'}))
    damageObservedDate       = forms.DateField(input_formats=["%d/%m/%Y"], label="Damage Observed Date", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Format - DD/MM/YYYY'}))
    damageOccuredDate        = forms.DateField(input_formats=["%d/%m/%Y"], label="Damage Occured Date", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Format - DD/MM/YYYY'}))
    notes                    = forms.CharField(label="Notes", widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))
    scheduledMaintenanceDate = forms.DateField(input_formats=["%d/%m/%Y"], label="Scheduled Maintenance Date", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Format - DD/MM/YYYY'}))
    damageImage              = forms.ImageField(label="Update Image", required=False, initial=r"images/asset_images/defaultImage.jpg")

    class Meta:
        model = Damage
        fields = [
            'damageType',
            'damageSeverity',
            'damageObservedDate',
            'damageOccuredDate',
            'notes',
            'scheduledMaintenanceDate',
            'damageImage',
        ]
