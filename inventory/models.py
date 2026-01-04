from django.db import models

# Create your models here.
class Listing(models.Model):
    class typeChoices(models.TextChoices):
        CONDO = "Condo", "Condo"
        VILLA = "Villa", "Villa"
        APARTMENT = "Apartment", "Apartment"
        PENTHOUSE = "Penthouse", "Penthouse"
        MANSION = "Mansion", "Mansion"
        WAREHOUSE = "Warehouse", "Warehouse"
        RETAIL_STORE = "Retail Store", "Retail Store"
        OFFICE_SPACE = "Office Space", "Office Space"

    class statusChoices(models.TextChoices):
        DRAFT = "Draft", "Draft"
        PENDING_GM_APPROVAL = "Pending GM Approval", "Pending GM Approval"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"
        ARCHIVED = "Archived", "Archived"

    id = models.CharField(max_length=10, primary_key=True)
    branch  = models.ForeignKey(
        'org.Branch',
        on_delete=models.CASCADE,
        related_name='listings'
    )
    type = models.TextField(
        max_length=20,
        choices=typeChoices.choices,
        default=typeChoices.APARTMENT)
    proposed_price = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=200)
    address = models.TextField()  
    city = models.CharField(max_length=100)
    status = models.TextField(
        max_length=30,
        choices=statusChoices.choices,
        default=statusChoices.DRAFT
    )
    gm_approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_listings'
    )
    gm_approved_at = models.DateTimeField(null=True, blank=True)
    gm_rejection_rsn = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.title} - {self.city} ({self.status})"