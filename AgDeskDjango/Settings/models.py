from django.db import models
from datetime import datetime, timedelta
from FarmAcc.models import FarmInfo
from django.contrib.auth.models import Group
from UserAuth.models import UserProfile
from FarmAcc.models import FarmInfo
from django.utils import timezone

# from UserAuth.models import User

class orgSettingsModel(models.Model):
    timezone = models.CharField(max_length=100)
    datetime_format = models.CharField(max_length=100)
    temperature_label = models.CharField(max_length=50)
    mass_label = models.CharField(max_length=50)
    area_label = models.CharField(max_length=50)
    length_label = models.CharField(max_length=50)


class internalTeamsModel(Group):
    """
    The internalTeam model is used to define teams which are situated within a specific farming tenant.
    """
    teamName = models.CharField(max_length=100)
    # creationDate = models.DateTimeField(default=)
    # teamModerator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    teamDescription = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)
    teamImage = models.ImageField(upload_to='images/internalTeams', default='images/internalTeams/default.jpg')
    farm = models.ForeignKey(FarmInfo, on_delete=models.SET_NULL, null=True)

class LinkingCode(models.Model):
    code = models.CharField(unique=True)
    farm = models.ForeignKey(FarmInfo, on_delete=models.CASCADE, related_name='linking_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Default expiry set to 12 hours after creation
            self.expires_at = datetime.now() + timedelta(hours=12)
        super().save(*args, **kwargs)
