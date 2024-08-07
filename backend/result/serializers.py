from rest_framework import serializers
from .models import Syllabus, ExamType, Exam, Result
from main.models import Student

class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = '__all__'

class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

    def validate(self, data):
        exam = data.get('exam')
        marks_obtained = data.get('marks_obtained')
        
        if marks_obtained < 0:
            raise serializers.ValidationError("Marks obtained cannot be negative.")
        if marks_obtained > exam.maximum_marks:
            raise serializers.ValidationError("Marks obtained cannot exceed maximum marks.")
        
        return data
    
    def get_student_name(self, obj):
        return obj.student.name  # Adjust based on the field name in the Student model

    def get_exam_name(self, obj):
        return f"{obj.exam.subject.name} ({obj.exam.exam_type.name})"  # Adjust based on the fields in Exam and ExamType models
