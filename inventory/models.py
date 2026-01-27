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

    class leadStatusChoices(models.TextChoices):
        PENDING = "Approval Pending", "Approval Pending"
        REJECTED = "Rejected", "Rejected"
        APPROVED = "Approved", "Approved"

    class oppStatusChoices(models.TextChoices):
        PROSPECTING = "Proespecting", "Prospecting"
        NEGOTIATING = "Negotiating", "Negotiating"
        PENDING = "Pending Approval", "Pending Approval"
        REJECTED = "Rejected", "Rejected"
        APPROVED = "Approved", "Approved"

    class saleStatusChoices(models.TextChoices):
        PROCESSING = "Processing", "Processing"
        CLOSED_WON = "Closed Won", "Closed Won"
        CLOSED_LOST = "Closed Lost", "Closed List"


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

    # Lead status fields
    lead_status = models.TextField(
        max_length=30,
        choices=leadStatusChoices.choices,
        default=leadStatusChoices.PENDING
    )
    lead_approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leads'
    )
    lead_approved_at = models.DateTimeField(null=True, blank=True)

    # Opportunity status fields
    opp_status = models.TextField(
        max_length=30,
        choices=oppStatusChoices.choices,
        default=oppStatusChoices.PENDING
    )
    opp_approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_opportunities'
    )
    opp_approved_at = models.DateTimeField(null=True, blank=True)

    # Sale status fields
    sale_status = models.TextField(
        max_length=30,
        choices=saleStatusChoices.choices,
        default=saleStatusChoices.PROCESSING
    )
    sale_closed_at = models.DateTimeField(null=True, blank=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    assigned_salesman = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_salesmen',
        limit_choices_to={'role': 'Salesman'},
    )
    comments = models.TextField(null=True, max_length=100, blank=True)


    def __str__(self):
        return f"{self.title} - {self.city} ({self.status})"