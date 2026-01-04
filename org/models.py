from django.db import models

# Create your models here.
class Branch(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    name  = models.CharField(max_length = 100)
    region = models.CharField(max_length = 100)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.region})"