from django.db import models


class Dorm(models.Model):
    """Dormitory model for managing residence halls."""
    
    class DormType(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        MIXED = 'mixed', 'Mixed'
    
    class DormStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        MAINTENANCE = 'maintenance', 'Maintenance'
        CLOSED = 'closed', 'Closed'
    
    dorm_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=DormType.choices)
    location = models.CharField(max_length=200, blank=True, null=True)
    total_rooms = models.PositiveIntegerField(blank=True, null=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    current_occupancy = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=DormStatus.choices,
        default=DormStatus.ACTIVE
    )
    proctor = models.ForeignKey(
        'accounts.Proctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_dorms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dorms'
        verbose_name = 'Dormitory'
        verbose_name_plural = 'Dormitories'
    
    def __str__(self):
        return f"{self.dorm_code} - {self.name}"


class Room(models.Model):
    """Room model for individual rooms within dormitories."""
    
    class RoomType(models.TextChoices):
        SINGLE = 'single', 'Single'
        DOUBLE = 'double', 'Double'
        TRIPLE = 'triple', 'Triple'
        QUAD = 'quad', 'Quad'
    
    class RoomStatus(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        OCCUPIED = 'occupied', 'Occupied'
        MAINTENANCE = 'maintenance', 'Maintenance'
        RESERVED = 'reserved', 'Reserved'
    
    dorm = models.ForeignKey(
        Dorm,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField(blank=True, null=True)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.DOUBLE
    )
    amenities = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rooms'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        unique_together = ['dorm', 'room_number']
    
    def __str__(self):
        return f"{self.dorm.dorm_code} - Room {self.room_number}"


class RoomInventory(models.Model):
    """Inventory items for each room."""
    
    class ItemCondition(models.TextChoices):
        GOOD = 'good', 'Good'
        DAMAGED = 'damaged', 'Damaged'
        MISSING = 'missing', 'Missing'
        NEEDS_REPAIR = 'needs_repair', 'Needs Repair'
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(
        max_length=20,
        choices=ItemCondition.choices,
        blank=True,
        null=True
    )
    last_check_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'room_inventory'
        verbose_name = 'Room Inventory Item'
        verbose_name_plural = 'Room Inventory Items'
    
    def __str__(self):
        return f"{self.room} - {self.item_name} ({self.quantity})"
