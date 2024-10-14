from django.db import models
from polymorphic.models import PolymorphicModel
from FarmAcc.models import FarmInfo
from UserAuth import *
import uuid

class AssetPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('asset', related_name='parts', on_delete=models.CASCADE)
    part_name = models.CharField(max_length=100, verbose_name="Part Name")
    hours_before_maintenance = models.PositiveIntegerField(verbose_name="Hours Before Maintenance")

    def __str__(self):
        return f"{self.part_name} ({self.hours_before_maintenance} hrs)"

    def __str__(self):
        return self.part_name
class asset(PolymorphicModel):
    assetPrefix      = models.CharField(max_length=2, null=False)
    assetID          = models.AutoField(primary_key=True)
    assetName        = models.CharField(max_length=100, null=False)
    farmID           = models.ForeignKey(FarmInfo, on_delete=models.CASCADE, null=False)
    Manufacturer     = models.CharField(max_length=100)
    # partsList        = models.CharField(max_length=255)
    Location         = models.CharField(max_length=100)
    dateManufactured = models.DateField(null=False)
    datePurchased    = models.DateField(null=False)
    deleted          = models.BooleanField(default=False)
    assetImage       = models.ImageField(upload_to="images/asset_images",
                                         default = "images/asset_images/defaultImage.jpg",
                                         null=False, blank=False)
    usageMinutes    = models.IntegerField(null=False, default=0)
    # Refactoring required:
    #     asset should also contain age, manufacturer, location, and parts list

    def __str__(self):
        return f"{self.assetID}-{self.assetPrefix} - {self.assetName}"


class vehicle(asset):
    vin = models.CharField(max_length=100, null=False)
    Registration = models.CharField(max_length=100)

    class Meta:
        abstract = True


class SmallEquipment(asset):
    """
    Small Equipment Class
    Small Equipment includes tools such as flashlights, drills, small generators, etc.
    """

    serialNumber = models.CharField(max_length=100, null=False)


class LargeEquipment(asset):
    """
    Large Equipment Class
    Large Equipment includes objects such as diesel generators, large pumps, and other large machinery.
    """

    vin = models.CharField(max_length=100, null=False)

#These need refactoring

class lightVehicle(vehicle):
    """
    Light Vehicle Class
    A Light Vehicle is any passenger vehicle such as a utility, sedan, or small truck.
    """

    currentlyInUse = models.BooleanField() # Remove?


class heavyVehicle(vehicle):
    """
    Heavy Vehicle Class
    A Heavy Vehicle can be anything such as a tactor, harvester, large truck or other large farm machinery.
    """

    inTransport = models.BooleanField()
    interFarmTransport = models.BooleanField()
