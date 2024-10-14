from django import forms
from django.forms import ModelForm
from . import models
from  .models import Maintenance
from .models import Expense
from assetMaintenance.models import Damage
from assetManagement.models import asset
from UserAuth.models import UserProfile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit,Row, Column, Div, HTML
from crispy_forms.bootstrap import Modal,StrictButton,PrependedText

class createExpenseForm(ModelForm):
    def __init__(self, user = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'expenseType', 'MaintenanceID', 'cost', 'receiptNumber', 'expenseLodgedBy',
            StrictButton("Close", css_class="btn btn-secondary float-left", data_bs_dismiss="modal"),
            StrictButton("Add Expense", type="submit", name='createExpense',css_class="btn custom-button float-right")
        )
        if user is not None:
            
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields["expenseType"].widget.attrs.update({"class": "form-control"})
            self.fields["MaintenanceID"].queryset = Maintenance.objects.filter(assetID = assetID, deleted = False)
            self.fields["cost"].widget.attrs.update({"class": "form-control"})
            self.fields["receiptNumber"].widget.attrs.update({"class": "form-control"})
            self.fields["expenseLodgedBy"].queryset = UserProfile.objects.filter(currentFarm_id  = currentFarmID)

    EXPENSE_TYPE_CHOICES = [
        (0, "Fuel"),
        (1, "Maintenance"),
        (2, "Insurance"),
        (3, "Registration"),
        (4, "Other")
    ]

    expenseType = forms.ChoiceField(choices = EXPENSE_TYPE_CHOICES, label="Expense Type", widget=forms.Select(attrs={'class': 'form-control'}))
    MaintenanceID = forms.ModelChoiceField(label="Maintenance Completed", queryset=Maintenance.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    cost = forms.DecimalField(max_digits=10, decimal_places=2, label="Cost", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    receiptNumber = forms.IntegerField(label="Receipt Number", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    expenseLodgedBy = forms.ModelChoiceField(label="Lodged By", queryset=UserProfile.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Expense
        fields = [
                    'expenseType', 
                    'MaintenanceID', 
                    'cost',
                    'receiptNumber',
                    'expenseLodgedBy']

class editExpenseForm(ModelForm):
    def __init__(self, user = None, assetID = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'expenseID','expenseType', 'MaintenanceID', 'cost', 'receiptNumber', 'expenseLodgedBy',
            StrictButton("Update", type="submit",name='Update',css_class="btn custom-button"),
            StrictButton("Delete", type="submit", name='Delete', css_class="btn btn-danger")
        )
        if user is not None:
            currentlyLoggedIn = UserProfile.objects.get(username = user)
            currentFarmID = currentlyLoggedIn.currentFarm_id

            self.fields['expenseID'].widget.attrs.update({"class": "form-control"})
            self.fields["expenseType"].widget.attrs.update({"class": "form-control"})
            self.fields["MaintenanceID"].queryset = Maintenance.objects.filter(assetID = assetID)
            self.fields["cost"].widget.attrs.update({"class": "form-control"})
            self.fields["receiptNumber"].widget.attrs.update({"class": "form-control"})
            self.fields["expenseLodgedBy"].queryset = UserProfile.objects.filter(currentFarm_id = currentFarmID)

    EXPENSE_TYPE_CHOICES = [
        (0, "Fuel"),
        (1, "Maintenance"),
        (2, "Insurance"),
        (3, "Registration"),
        (4, "Other")
    ]
    expenseID = forms.IntegerField(widget=forms.HiddenInput())
    expenseType = forms.ChoiceField(choices = EXPENSE_TYPE_CHOICES, label="Expense Type", widget=forms.Select(attrs={'class': 'form-control'}))
    MaintenanceID = forms.ModelChoiceField(label="Maintenance Completed", queryset=Maintenance.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    cost = forms.DecimalField(max_digits=10, decimal_places=2, label="Cost", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    receiptNumber = forms.IntegerField(label="Receipt Number", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    expenseLodgedBy = forms.ModelChoiceField(label="Lodged By", queryset=UserProfile.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Expense
        fields = ['expenseID',
                    'expenseType', 
                    'MaintenanceID', 
                    'cost',
                    'receiptNumber',
                    'expenseLodgedBy']
                                
