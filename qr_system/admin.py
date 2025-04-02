from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, QRCode, EmergencyInfo

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('created_at',)}),
    )

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('qr_code_data', 'assigned_to', 'is_assigned', 'created_at')
    search_fields = ('qr_code_data', 'assigned_to__email')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(EmergencyInfo)
class EmergencyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'blood_type', 'updated_at')
    search_fields = ('name', 'user__email', 'medical_conditions')
    list_filter = ('blood_type', 'updated_at')
    readonly_fields = ('updated_at',)