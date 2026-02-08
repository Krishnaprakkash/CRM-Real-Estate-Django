from django.db import models

# Create your models here.
class Listing(models.Model):
    class typeChoices(models.TextChoices):
        VILLA = "Villa", "Villa"
        APARTMENT = "Apartment", "Apartment"
        WAREHOUSE = "Warehouse", "Warehouse"
        RETAIL_STORE = "Retail", "Retail Store"
        OFFICE_SPACE = "Office", "Office Space"

    class leadStatusChoices(models.TextChoices):
        PENDING = "Pending", "Pending Approval"
        REJECTED = "Rejected", "Rejected"
        APPROVED = "Approved", "Approved"

    class oppStatusChoices(models.TextChoices):
        PROSPECTING = "Prospecting", "Prospecting"
        NEGOTIATING = "Negotiating", "Negotiating"
        PENDING = "Pending", "Pending Approval"
        REJECTED = "Rejected", "Rejected"
        APPROVED = "Approved", "Approved"

    class saleStatusChoices(models.TextChoices):
        PROCESSING = "Processing", "Processing"
        CLOSED_WON = "ClosedW", "Closed Won"
        CLOSED_LOST = "ClosedL", "Closed Lost"


    id = models.CharField(max_length=10, primary_key=True)
    branch  = models.ForeignKey(
        'org.Branch',
        on_delete=models.CASCADE,
        related_name='listings'
    )
    type = models.TextField(
        choices=typeChoices.choices,
        default=typeChoices.APARTMENT)
    proposed_price = models.DecimalField(max_digits=12, decimal_places=2)
    title = models.CharField(max_length=200)
    address = models.TextField()  
    city = models.CharField(max_length=100)

    # Lead status fields
    lead_status = models.TextField(
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
        choices=oppStatusChoices.choices,
        null=True, blank=True
    )
    opp_approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_opportunities'
    )
    opp_approved_at = models.DateTimeField(null=True, blank=True)
    opp_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Sale status fields
    sale_status = models.TextField(
        choices=saleStatusChoices.choices,
        null=True, blank=True
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
    comments = models.CharField(null=True, max_length=100, blank=True)

    def __str__(self):
        return f"{self.title} - {self.city}"

    def get_property_details(self):
        """Returns the related property-specific details"""
        detail_map = {
            self.typeChoices.VILLA: 'villa_details',
            self.typeChoices.APARTMENT: 'apartment_details',
            self.typeChoices.WAREHOUSE: 'warehouse_details',
            self.typeChoices.RETAIL_STORE: 'retail_details',
            self.typeChoices.OFFICE_SPACE: 'office_details',
        }
        related_name = detail_map.get(self.type)
        if related_name:
            try:
                return getattr(self, related_name, None)
            except AttributeError:
                return None
        return None
    
    @property
    def current_stage(self):
        if self.sale_status:
            if self.sale_status == Listing.saleStatusChoices.CLOSED_WON:
                return 'closed_won'
            elif self.sale_status == Listing.saleStatusChoices.CLOSED_LOST:
                return 'closed_lost'
            else:
                return 'processing'
            
        elif self.opp_status:
            if self.opp_status == self.oppStatusChoices.PROSPECTING:
                return 'prospecting'
            elif self.opp_status == self.oppStatusChoices.NEGOTIATING:
                return 'negotiating'
            else:
                return 'final_approval'
            
        elif self.lead_status:
            if self.lead_status == Listing.leadStatusChoices.PENDING:
                return 'created'
            else:
                return 'first_approval'
        return 'created'
    
    @property
    def stage_display(self):
        stage_names = {
            'closed_won': 'Closed Won',
            'closed_lost': 'Closed Lost',
            'processing': 'Processing',
            'prospecting': 'Prospecting',
            'negotiating': 'Negotiating',
            'final_approval': 'Final Approval',
            'created': 'Created',
            'first_approval': 'First Approval'
        }
        return stage_names.get(self.current_stage, 'Unknown')


# ============================================
# Property-Specific Detail Models
# ============================================

class VillaDetails(models.Model):
    """Villa-specific fields"""
    
    class BHKChoices(models.TextChoices):
        ONE = "1BHK", "1 BHK"
        TWO = "2BHK", "2 BHK"
        THREE = "3BHK", "3 BHK"
        FOUR = "4BHK", "4 BHK"
        FIVE = "5BHK", "5 BHK"
        FIVE_PLUS = "5+BHK", "5+ BHK"
    
    class FurnishingChoices(models.TextChoices):
        UNFURNISHED = "unfurnished", "Unfurnished"
        SEMI = "semi", "Semi-Furnished"
        FULLY = "fully", "Fully Furnished"
    
    class FacingChoices(models.TextChoices):
        NORTH = "N", "North"
        SOUTH = "S", "South"
        EAST = "E", "East"
        WEST = "W", "West"
        NORTH_EAST = "NE", "North-East"
        NORTH_WEST = "NW", "North-West"
        SOUTH_EAST = "SE", "South-East"
        SOUTH_WEST = "SW", "South-West"
    
    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='villa_details'
    )
    
    # Configuration
    bhk_config = models.CharField(max_length=10, choices=BHKChoices.choices)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    
    # Area
    plot_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    built_up_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    carpet_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Structure
    number_of_floors = models.PositiveIntegerField(default=1)
    furnishing_status = models.CharField(max_length=15, choices=FurnishingChoices.choices)
    facing = models.CharField(max_length=5, choices=FacingChoices.choices)
    
    # Parking
    parking_available = models.BooleanField(default=False)
    covered_parking_spaces = models.PositiveIntegerField(default=0)
    open_parking_spaces = models.PositiveIntegerField(default=0)
    
    # Amenities
    swimming_pool = models.BooleanField(default=False)
    private_garden = models.BooleanField(default=False)
    servant_quarters = models.BooleanField(default=False)
    power_backup = models.BooleanField(default=False)
    security_24x7 = models.BooleanField(default=False)
    gated_community = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Villa Details for {self.listing.title}"


class ApartmentDetails(models.Model):
    """Apartment-specific fields"""
    
    class BHKChoices(models.TextChoices):
        STUDIO = "studio", "Studio"
        ONE = "1BHK", "1 BHK"
        ONE_HALF = "1.5BHK", "1.5 BHK"
        TWO = "2BHK", "2 BHK"
        TWO_HALF = "2.5BHK", "2.5 BHK"
        THREE = "3BHK", "3 BHK"
        FOUR = "4BHK", "4 BHK"
        FOUR_PLUS = "4+BHK", "4+ BHK"
        PENTHOUSE = "penthouse", "Penthouse"
    
    class FurnishingChoices(models.TextChoices):
        UNFURNISHED = "unfurnished", "Unfurnished"
        SEMI = "semi", "Semi-Furnished"
        FULLY = "fully", "Fully Furnished"
    
    class ParkingChoices(models.TextChoices):
        NONE = "none", "No Parking"
        OPEN = "open", "Open Parking"
        COVERED = "covered", "Covered Parking"
        BASEMENT = "basement", "Basement Parking"
    
    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='apartment_details'
    )
    
    # Configuration
    bhk_config = models.CharField(max_length=15, choices=BHKChoices.choices)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    balconies = models.PositiveIntegerField(default=0)
    
    # Area
    carpet_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    built_up_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    super_built_up_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Floor
    floor_number = models.IntegerField()
    total_floors = models.PositiveIntegerField()
    tower = models.CharField(max_length=10, blank=True)
    unit_number = models.CharField(max_length=20, blank=True)
    
    # Parking
    parking_type = models.CharField(max_length=15, choices=ParkingChoices.choices)
    parking_spaces = models.PositiveIntegerField(default=0)
    
    # Furnishing
    furnishing_status = models.CharField(max_length=15, choices=FurnishingChoices.choices)
    
    # Amenities
    lift_available = models.BooleanField(default=False)
    power_backup = models.BooleanField(default=False)
    swimming_pool = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    clubhouse = models.BooleanField(default=False)
    security_24x7 = models.BooleanField(default=False)
    
    # Charges
    maintenance_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    def __str__(self):
        return f"Apartment Details for {self.listing.title}"


class WarehouseDetails(models.Model):
    """Warehouse-specific fields"""
    
    class FloorTypeChoices(models.TextChoices):
        CONCRETE = "concrete", "RCC/Concrete"
        EPOXY = "epoxy", "Epoxy Coated"
        VDF = "vdf", "VDF"
        TREMIX = "tremix", "Tremix"
    
    class StructureChoices(models.TextChoices):
        RCC = "rcc", "RCC"
        PEB = "peb", "Pre-Engineered Building (PEB)"
        SHED = "shed", "Industrial Shed"
    
    class FireSystemChoices(models.TextChoices):
        NONE = "none", "None"
        EXTINGUISHER = "extinguisher", "Fire Extinguishers"
        HYDRANT = "hydrant", "Fire Hydrant"
        SPRINKLER = "sprinkler", "Sprinkler System"
        BOTH = "both", "Hydrant + Sprinkler"
    
    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='warehouse_details'
    )
    
    # Area
    total_area_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    covered_area_sqft = models.DecimalField(max_digits=12, decimal_places=2)
    open_area_sqft = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    office_area_sqft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    # Structure
    ceiling_height_ft = models.DecimalField(max_digits=6, decimal_places=2)
    floor_type = models.CharField(max_length=15, choices=FloorTypeChoices.choices)
    structure_type = models.CharField(max_length=15, choices=StructureChoices.choices)
    floor_load_capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Access
    loading_docks = models.PositiveIntegerField(default=0)
    ground_level_doors = models.PositiveIntegerField(default=0)
    truck_accessible = models.BooleanField(default=True)
    container_accessible = models.BooleanField(default=False)
    
    # Power
    power_load_kva = models.DecimalField(max_digits=8, decimal_places=2)
    three_phase_power = models.BooleanField(default=True)
    power_backup = models.BooleanField(default=False)
    
    # Safety
    fire_system_type = models.CharField(max_length=15, choices=FireSystemChoices.choices)
    fire_noc = models.BooleanField(default=False)
    
    # Special Features
    cold_storage = models.BooleanField(default=False)
    hazmat_approved = models.BooleanField(default=False)
    
    # Parking
    truck_parking_spaces = models.PositiveIntegerField(default=0)
    car_parking_spaces = models.PositiveIntegerField(default=0)
    
    # Security
    security_24x7 = models.BooleanField(default=False)
    cctv = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Warehouse Details for {self.listing.title}"


class RetailDetails(models.Model):
    """Retail Store-specific fields"""
    
    class FloorChoices(models.TextChoices):
        BASEMENT = "basement", "Basement"
        GROUND = "ground", "Ground Floor"
        FIRST = "first", "First Floor"
        SECOND = "second", "Second Floor"
        UPPER = "upper", "Upper Floors"
    
    class LocationTypeChoices(models.TextChoices):
        HIGH_STREET = "high_street", "High Street"
        MALL = "mall", "Shopping Mall"
        MARKET = "market", "Market Complex"
        STANDALONE = "standalone", "Standalone"
    
    class FootfallChoices(models.TextChoices):
        LOW = "low", "Low (<100/day)"
        MODERATE = "moderate", "Moderate (100-500/day)"
        HIGH = "high", "High (500-2000/day)"
        VERY_HIGH = "very_high", "Very High (2000+/day)"
    
    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='retail_details'
    )
    
    # Area
    carpet_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    frontage_ft = models.DecimalField(max_digits=6, decimal_places=2)
    ceiling_height_ft = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Floor
    floor_location = models.CharField(max_length=20, choices=FloorChoices.choices)
    mezzanine_available = models.BooleanField(default=False)
    
    # Location
    location_type = models.CharField(max_length=20, choices=LocationTypeChoices.choices)
    mall_name = models.CharField(max_length=100, blank=True)
    
    # Storefront
    display_window = models.BooleanField(default=False)
    corner_shop = models.BooleanField(default=False)
    main_road_facing = models.BooleanField(default=False)
    
    # Facilities
    storage_room = models.BooleanField(default=False)
    attached_restroom = models.BooleanField(default=False)
    
    # Power
    power_load_kw = models.DecimalField(max_digits=6, decimal_places=2)
    air_conditioning = models.BooleanField(default=False)
    power_backup = models.BooleanField(default=False)
    
    # Parking
    dedicated_parking = models.PositiveIntegerField(default=0)
    common_parking_available = models.BooleanField(default=False)
    
    # Signage
    external_signage_allowed = models.BooleanField(default=True)
    
    # Suitability
    food_license_possible = models.BooleanField(default=True)
    estimated_footfall = models.CharField(max_length=15, choices=FootfallChoices.choices)
    
    # Charges
    maintenance_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    def __str__(self):
        return f"Retail Details for {self.listing.title}"


class OfficeDetails(models.Model):
    """Office Space-specific fields"""
    
    class OfficeTypeChoices(models.TextChoices):
        BARE = "bare", "Bare Shell"
        WARM = "warm", "Warm Shell"
        FITTED = "fitted", "Fully Fitted"
        PLUG_PLAY = "plug_play", "Plug & Play"
        COWORKING = "coworking", "Co-working"
    
    class FurnishingChoices(models.TextChoices):
        UNFURNISHED = "unfurnished", "Unfurnished"
        SEMI = "semi", "Semi-Furnished"
        FULLY = "fully", "Fully Furnished"
    
    class BuildingGradeChoices(models.TextChoices):
        A_PLUS = "A+", "Grade A+"
        A = "A", "Grade A"
        B_PLUS = "B+", "Grade B+"
        B = "B", "Grade B"
        C = "C", "Grade C"
    
    class ParkingChoices(models.TextChoices):
        NONE = "none", "No Parking"
        OPEN = "open", "Open"
        COVERED = "covered", "Covered"
        BASEMENT = "basement", "Basement"
        MULTILEVEL = "multilevel", "Multi-level"
    
    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='office_details'
    )
    
    # Type & Configuration
    office_type = models.CharField(max_length=15, choices=OfficeTypeChoices.choices)
    furnishing_status = models.CharField(max_length=15, choices=FurnishingChoices.choices)
    workstation_capacity = models.PositiveIntegerField()
    
    # Area
    carpet_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    built_up_area_sqft = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Layout
    number_of_cabins = models.PositiveIntegerField(default=0)
    conference_rooms = models.PositiveIntegerField(default=0)
    meeting_rooms = models.PositiveIntegerField(default=0)
    reception_area = models.BooleanField(default=False)
    
    # Floor
    floor_number = models.IntegerField()
    total_floors = models.PositiveIntegerField()
    building_name = models.CharField(max_length=100, blank=True)
    building_grade = models.CharField(max_length=5, choices=BuildingGradeChoices.choices)
    
    # Facilities
    pantry = models.BooleanField(default=False)
    cafeteria = models.BooleanField(default=False)
    server_room = models.BooleanField(default=False)
    
    # Parking
    parking_type = models.CharField(max_length=15, choices=ParkingChoices.choices)
    car_parking_spaces = models.PositiveIntegerField(default=0)
    
    # Power & Utilities
    power_load_kva = models.DecimalField(max_digits=8, decimal_places=2)
    power_backup = models.BooleanField(default=False)
    central_ac = models.BooleanField(default=False)
    
    # IT
    fiber_optic = models.BooleanField(default=False)
    
    # Access
    access_24x7 = models.BooleanField(default=False)
    lifts = models.PositiveIntegerField(default=0)
    
    # Security
    security_24x7 = models.BooleanField(default=False)
    fire_safety_system = models.BooleanField(default=False)
    
    # Charges
    maintenance_per_sqft = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    
    def __str__(self):
        return f"Office Details for {self.listing.title}"
