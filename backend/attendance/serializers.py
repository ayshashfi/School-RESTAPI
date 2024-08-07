from rest_framework import serializers
from main.models import Student
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, data):
        student = data.get('student')
        date = data.get('date')

        if Attendance.objects.filter(student=student, date=date).exists():
            raise serializers.ValidationError(
                {"unique": "Attendance already marked."}
            )

        return data