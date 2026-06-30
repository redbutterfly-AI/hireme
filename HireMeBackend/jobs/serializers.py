from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.username', read_only=True)
    employer_id   = serializers.IntegerField(source='employer.id', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['employer', 'status', 'created_at']