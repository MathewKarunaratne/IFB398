from django.db import models

class FarmInfo(models.Model):
    farm_name = models.CharField(max_length=100)
    farm_street = models.CharField(max_length=100)
    farm_state = models.CharField(max_length=20)
    farm_postcode = models.CharField(max_length=6)
    farm_address = str(farm_street) + ", " + str(farm_state) + ", " + str(farm_postcode)
    farm_bio = models.TextField()
    farm_image = models.ImageField(upload_to="images/farm_images", default = "images/farm_images/default_image.png", blank=True, null=True)

    def __str__(self):
        return self.farm_name

class FileCategory(models.Model):
    """
    The following enables users to define categories to assign documents to.
    """
    # File Category Attributes 
    fileCategoryName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.fileCategoryName

 
class FileRecord(models.Model):
    """
    The FileRecord model is used to store farm related documents within the Django application, which
    farmers can set review dates for. When a new File Record is instantiated, it is uploaded under the 
    'files' directory within the media folder.
    """
    # File Record Attributes
    fileName = models.CharField(max_length=100)
    reviewDate = models.DateField(null=True)
    file = models.FileField(upload_to="files/")
    fileCategory = models.ForeignKey(FileCategory, on_delete=models.SET_NULL,  null=True, blank=True)


