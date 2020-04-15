from rest_framework import serializers

from .models import Company, Department, StatTitle, Stat


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    departments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'title', 'slug', 'departments']


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    stat_titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'title', 'slug', 'overview', 'stat_titles']


class StatTitleSerializer(serializers.HyperlinkedModelSerializer):
    stats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = StatTitle
        fields = ['id', 'title', 'overview', 'stats']


class StatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stat
        fields = ['id', 'amount', 'date']
