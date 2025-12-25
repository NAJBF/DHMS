from django.contrib import admin
from .models import Dorm, Room, RoomInventory


class RoomInline(admin.TabularInline):
    """Inline admin for rooms within a dorm."""
    model = Room
    extra = 0
    fields = ('room_number', 'floor', 'capacity', 'current_occupancy', 'room_type', 'status')
    readonly_fields = ('current_occupancy',)


class RoomInventoryInline(admin.TabularInline):
    """Inline admin for inventory items within a room."""
    model = RoomInventory
    extra = 0
    fields = ('item_name', 'quantity', 'condition', 'last_check_date')


@admin.register(Dorm)
class DormAdmin(admin.ModelAdmin):
    """Admin configuration for Dorm model."""
    
    list_display = ('dorm_code', 'name', 'type', 'location', 'total_rooms', 
                    'capacity', 'current_occupancy', 'status', 'proctor')
    list_filter = ('type', 'status')
    search_fields = ('dorm_code', 'name', 'location')
    raw_id_fields = ('proctor',)
    readonly_fields = ('current_occupancy', 'created_at')
    inlines = [RoomInline]
    
    fieldsets = (
        (None, {'fields': ('dorm_code', 'name', 'type')}),
        ('Location & Capacity', {'fields': ('location', 'total_rooms', 'capacity', 'current_occupancy')}),
        ('Management', {'fields': ('status', 'proctor')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin configuration for Room model."""
    
    list_display = ('get_room_display', 'dorm', 'floor', 'capacity', 
                    'current_occupancy', 'room_type', 'status')
    list_filter = ('dorm', 'room_type', 'status', 'floor')
    search_fields = ('room_number', 'dorm__name', 'dorm__dorm_code')
    raw_id_fields = ('dorm',)
    readonly_fields = ('current_occupancy', 'created_at')
    inlines = [RoomInventoryInline]
    
    fieldsets = (
        (None, {'fields': ('dorm', 'room_number', 'floor')}),
        ('Capacity & Type', {'fields': ('capacity', 'current_occupancy', 'room_type')}),
        ('Details', {'fields': ('amenities', 'status')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    @admin.display(description='Room')
    def get_room_display(self, obj):
        return f"{obj.dorm.dorm_code} - {obj.room_number}"


@admin.register(RoomInventory)
class RoomInventoryAdmin(admin.ModelAdmin):
    """Admin configuration for RoomInventory model."""
    
    list_display = ('item_name', 'room', 'quantity', 'condition', 'last_check_date')
    list_filter = ('condition', 'room__dorm')
    search_fields = ('item_name', 'room__room_number', 'room__dorm__name')
    raw_id_fields = ('room',)
    
    fieldsets = (
        (None, {'fields': ('room', 'item_name', 'quantity')}),
        ('Condition', {'fields': ('condition', 'last_check_date', 'notes')}),
    )
