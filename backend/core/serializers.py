"""
Core serializers for system-wide functionality
"""
from rest_framework import serializers
from .models import Unit, ImportSession


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Unit model"""
    
    class Meta:
        model = Unit
        fields = ['id', 'code', 'name', 'is_system', 'created_at']
        read_only_fields = ['is_system', 'created_at']

    def validate_code(self, value):
        """Ensure code is uppercase and unique"""
        code = value.upper().strip()
        
        # Check for duplicates (excluding current instance on update)
        queryset = Unit.objects.filter(code=code)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(f"Unit with code '{code}' already exists.")
        
        return code


class ImportSessionSerializer(serializers.ModelSerializer):
    """Serializer for ImportSession model"""
    user_name = serializers.SerializerMethodField()
    can_undo = serializers.ReadOnlyField()
    undo_time_remaining = serializers.ReadOnlyField()
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ImportSession
        fields = [
            'id', 'entity_type', 'entity_type_display', 'user', 'user_name',
            'file_name', 'total_rows', 'success_count', 'error_count', 
            'duplicate_count', 'status', 'status_display', 'created_at', 
            'undone_at', 'undo_expires_at', 'can_undo', 'undo_time_remaining'
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'undone_at', 'undo_expires_at'
        ]

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return 'Unknown'


class ImportSessionDetailSerializer(ImportSessionSerializer):
    """Detailed serializer including error information"""
    imported_ids = serializers.ReadOnlyField()
    errors = serializers.ReadOnlyField()

    class Meta(ImportSessionSerializer.Meta):
        fields = ImportSessionSerializer.Meta.fields + ['imported_ids', 'errors']
