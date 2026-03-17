from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        CEO = "CEO", "CEO",
        MANAGER = "Manager", "Manager",
        SALESMAN = "Salesman", "Salesman"
        
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SALESMAN
    )
    branch = models.ForeignKey(
        'org.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': Role.MANAGER},
        related_name='salesmen'
    )

    def __str__(self):
        return self.get_username()
