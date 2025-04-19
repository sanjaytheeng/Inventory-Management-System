from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import InventoryItem, Assignment, Agent

class BaseAdmin(admin.ModelAdmin):
    def get_actions_column(self, obj):
        if not obj or not hasattr(obj, 'id'):
            return '-'
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary" title="Edit"><i class="fas fa-edit"></i></a> '
            '<a href="{}" class="btn btn-sm btn-outline-danger" title="Delete"><i class="fas fa-trash-alt"></i></a>'
            '</div>',
            reverse('admin:core_{}_change'.format(self.model._meta.model_name), args=[obj.id]),
            reverse('admin:core_{}_delete'.format(self.model._meta.model_name), args=[obj.id])
        )
    get_actions_column.short_description = 'Actions'

@admin.register(InventoryItem)
class InventoryItemAdmin(BaseAdmin):
    list_display = ('name', 'category', 'total_quantity', 'in_use_quantity', 'available_quantity', 'unit_price', 'created_at', 'updated_at', 'get_actions_column')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('in_use_quantity', 'available_quantity', 'created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Quantity Information', {
            'fields': ('total_quantity', 'in_use_quantity', 'available_quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Assignment)
class AssignmentAdmin(BaseAdmin):
    list_display = ('inventory_item', 'agent_name', 'quantity', 'assigned_date', 'return_date', 'status', 'created_at', 'updated_at', 'get_actions_column')
    list_filter = ('status', 'assigned_date', 'return_date', 'created_at', 'updated_at')
    search_fields = ('inventory_item__name', 'agent_name', 'remarks')
    readonly_fields = ('assigned_date', 'created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Assignment Details', {
            'fields': ('inventory_item', 'agent_name', 'quantity')
        }),
        ('Status Information', {
            'fields': ('status', 'return_date', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('assigned_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Agent)
class AgentAdmin(BaseAdmin):
    list_display = ('name', 'contact_info', 'contact_number', 'email', 'created_at', 'updated_at', 'get_actions_column')
    search_fields = ('name', 'contact_info', 'contact_number', 'email')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name',)
        }),
        ('Contact Information', {
            'fields': ('contact_info', 'contact_number', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
