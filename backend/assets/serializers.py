from rest_framework import serializers
from .models import Asset, AssetLog

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'
        extra_kwargs = {
            'purchase_value': {'min_value': 0},
            'current_value': {'min_value': 0},
        }

class AssetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLog
        fields = '__all__' 