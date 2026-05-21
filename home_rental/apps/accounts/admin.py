from django.contrib import admin
from django.contrib.auth.models import User as DjangoUser

# Re-register Django default user with more fields
admin.site.unregister(DjangoUser)

@admin.register(DjangoUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display  = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    list_filter   = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering      = ['-date_joined']