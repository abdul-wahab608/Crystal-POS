from rest_framework import serializers
from .models import Asset, AssetLog

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class AssetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLog
        fields = '__all__' 