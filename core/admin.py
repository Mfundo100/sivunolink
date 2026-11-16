from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    User, FarmProfile, DriverProfile, ProduceListing, Order, OrderItem, 
    EscrowTransaction, AuditLog, OTPRecord, Rating, PlatformSetting, 
    PaymentTransaction, OrderFulfilment
)

class CustomUserAdmin(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'phone_number', 'is_verified', 'preferred_language', 'is_available')}),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('SivunoLink Profile', {'fields': ('role', 'phone_number', 'is_verified', 'preferred_language', 'is_available')}),
    )
    list_display = ['username', 'email', 'role', 'phone_number', 'is_verified', 'is_available']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'matched_driver', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(OrderFulfilment)
class OrderFulfilmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'farmer', 'status', 'gross_amount', 'net_amount')
    list_filter = ('status',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'order', 'method', 'status', 'amount', 'created_at')
    list_filter = ('status', 'method')

@admin.register(PlatformSetting)
class PlatformSettingAdmin(admin.ModelAdmin):
    list_display = ('commission_rate', 'updated_at')

# Register the rest simply
admin.site.register(FarmProfile)
admin.site.register(DriverProfile)
admin.site.register(ProduceListing)
admin.site.register(EscrowTransaction)
admin.site.register(AuditLog)
admin.site.register(OTPRecord)
admin.site.register(Rating)
admin.site.register(OrderItem)
admin.site.register(User, CustomUserAdmin)
