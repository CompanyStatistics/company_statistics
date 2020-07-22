from rest_framework import serializers

from .models import Company, Department, StatTitle, Stat


class CompanySerializer(serializers.ModelSerializer):
    departments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    stat_titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class StatTitleSerializer(serializers.ModelSerializer):
    stats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = StatTitle
        fields = '__all__'


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = '__all__'
