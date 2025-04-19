from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserActivity

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 20
    date_hierarchy = 'date_joined'
    ordering = ('-date_joined',)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('created_at',)
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
