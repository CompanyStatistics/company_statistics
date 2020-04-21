from rest_framework import serializers

from .models import Company, Department, StatTitle, Stat


# class CompanySerializer(serializers.HyperlinkedModelSerializer):
class CompanySerializer(serializers.ModelSerializer):
    departments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        # fields = ['id', 'title', 'slug', 'departments']
        fields = '__all__'


# class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
class DepartmentSerializer(serializers.Serializer):
    stat_titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Department
        # fields = ['id', 'title', 'slug', 'overview', 'stat_titles']
        fields = '__all__'


# class StatTitleSerializer(serializers.HyperlinkedModelSerializer):
class StatTitleSerializer(serializers.ModelSerializer):
    stats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = StatTitle
        # fields = ['id', 'title', 'overview', 'stats']
        fields = '__all__'


# class StatSerializer(serializers.HyperlinkedModelSerializer):
class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        # fields = ['id', 'amount', 'date']
        fields = '__all__'
