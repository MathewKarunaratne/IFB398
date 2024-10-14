"""
Forms required for the check out check in system, the operation logs, and the performance metrics.
"""

# Imports
from django.forms import ModelForm, HiddenInput
from django import forms

from .models import OperationLog#, PerformanceMetric, OperationLogMetric


# Constants
NOTES_LABEL = "Notes (Optional)" # Change once, change everywhere


# Check Out Check In Forms
class checkOutForm(ModelForm):
    """
    Form for checking out an asset.
    assetID/Prefix to map to the correct foreign key.
    The view will also populate userID and startDateTime.
    """

    class Meta:
        model  = OperationLog
        fields = ["assetID", "location", "notes"]

    assetID     = forms.IntegerField(label="assetID", widget=HiddenInput())
    location    = forms.CharField(label="Location",widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes       = forms.CharField(label=NOTES_LABEL, required=False, widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'}))



class checkInForm(ModelForm):
    """
    Form for checking back in an asset.
    logID to update the correct log to its final state.
    The view will also populate endDateTime.
    """

    class Meta:
        model = OperationLog
        fields = ["logID", "notes"]

    logID = forms.IntegerField(widget=HiddenInput())
    location    = forms.CharField(label="Location",widget=forms.TextInput(attrs={'class': 'form-control'}))
    # Separate fields for hours and minutes for usage
    usage_hours = forms.IntegerField(label="Usage Hours", min_value=0, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    usage_minutes = forms.IntegerField(label="Usage Minutes", min_value=0, max_value=59, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    notes = forms.CharField(
        label="Notes", 
        required=False, 
        widget=forms.Textarea(attrs={"cols": 40, "rows": 6, 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('usage_hours')
        minutes = cleaned_data.get('usage_minutes')
        
        # Convert hours and minutes to total minutes and set it to `usage`
        total_usage_minutes = (hours * 60) + minutes
        cleaned_data['usage'] = total_usage_minutes
        
        return cleaned_data


# Operation Log Forms
# later


# Performance Metric Forms
# later
