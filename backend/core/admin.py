"""
Core admin configuration
"""
from django.contrib import admin
from .models import Unit, ImportSession


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_system', 'created_at']
    list_filter = ['is_system']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at']
    ordering = ['name']


@admin.register(ImportSession)
class ImportSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'entity_type', 'file_name', 'user',
        'total_rows', 'success_count', 'error_count', 
        'status', 'created_at', 'can_undo'
    ]
    list_filter = ['entity_type', 'status', 'created_at']
    search_fields = ['file_name', 'user__username']
    readonly_fields = [
        'id', 'created_at', 'undone_at', 'undo_expires_at',
        'imported_ids', 'errors', 'can_undo', 'undo_time_remaining'
    ]
    ordering = ['-created_at']
    
    def can_undo(self, obj):
        return obj.can_undo
    can_undo.boolean = True
