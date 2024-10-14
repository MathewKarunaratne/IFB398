"""
Models required for the check out check in system, the operation logs, and the performance metrics.
The check out check in system uses the operation log model.
"""

# Imports
from datetime import datetime
from django.db import models


# Check Out Check In & Operation Log Model
class OperationLog(models.Model):
    logID         = models.AutoField(primary_key=True)
    assetID       = models.ForeignKey("assetManagement.asset", on_delete=models.CASCADE)
    userID        = models.ForeignKey("UserAuth.UserProfile", on_delete=models.CASCADE)

    startDateTime = models.DateTimeField(default=datetime.now)
    endDateTime   = models.DateTimeField(null=True, blank=True)

    location      = models.CharField(max_length=64)
    notes         = models.CharField(max_length=256, null=True, blank=True)
    usageHours    = models.IntegerField(null=False, default=0)
    usageMinutes    = models.IntegerField(null=False, default=0)
    deleted       = models.BooleanField(default=False)

# Foreign key on_delete should probably be SET() or DO_NOTHING for logs. Logs can outlast assets.


# Performance Metric Models
class PerformanceMetric(models.Model):
    metricID    = models.AutoField(primary_key=True)
    assetID     = models.ForeignKey("assetManagement.asset", on_delete=models.CASCADE)

    name        = models.CharField(max_length=32)
    deleted     = models.BooleanField(default=False)


class OperationLogMetric(models.Model):
    logMetricID = models.AutoField(primary_key=True)
    logID       = models.ForeignKey("OperationLog", on_delete=models.CASCADE)
    metricID    = models.ForeignKey("PerformanceMetric", on_delete=models.RESTRICT)

    value       = models.DecimalField(max_digits=14, decimal_places=4)
    # Doesn't need own deleted, treat as deleted if either logID or metricID has deleted=True
