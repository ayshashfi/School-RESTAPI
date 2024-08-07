from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import serializers
from .models import TeacherFile, User, Student, Teacher, ClassRoom, Subject
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'date_of_birth', 'address', 'phone_number', 'is_student', 'is_teacher', 'is_admin', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PasswordResetSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uid']))
        token = self.validated_data['token']
        password = self.validated_data['password']

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(password)
            user.is_active = True  
            user.save()
        else:
            raise serializers.ValidationError("Invalid token or user.")

        return user


class ClassroomSerializer(serializers.ModelSerializer):

    # teacher = TeacherSerializer()

    class Meta:
        model = ClassRoom
        fields = ['id', 'class_no', 'section', 'class_teacher', 'class_strength', 'syllabus_count']

    def validate(self, attrs):
        if self.instance: 
            if ClassRoom.objects.filter(class_no=attrs.get('class_no'), section=attrs.get('section')).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("ClassRoom with this Class No and Section already exists.")
        else: 
            if ClassRoom.objects.filter(class_no=attrs.get('class_no'), section=attrs.get('section')).exists():
                raise serializers.ValidationError("ClassRoom with this Class No and Section already exists.")

        return attrs
    
class StudentSerializer(serializers.ModelSerializer):
    class_room = ClassroomSerializer
    class Meta:
        model = Student
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'date_of_birth', 'address', 'phone_number', 'profile_picture', 'is_student', 'is_teacher', 'is_admin', 'is_active', 'admission_date', 'parent_contact', 'class_room', 'roll_no']

    def create(self, validated_data):
        student = Student.objects.create(**validated_data)
        
        if 'password' in validated_data:
            student.set_password(validated_data['password'])
        student.is_student = True
        student.save()
        
        return student 
  
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = '__all__'

class TeacherFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherFile
        fields = '__all__'
        
class TeacherSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    files = TeacherFileSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'date_of_birth', 'address', 'phone_number', 'profile_picture', 'is_student', 'is_teacher', 'is_admin', 'is_active', 'joined_date', 'subject', 'files']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        subject_data = validated_data.pop('subject')
        teacher = Teacher.objects.create(**validated_data)
        if 'password' in validated_data:
            teacher.set_password(validated_data['password'])
        teacher.is_teacher = True
        teacher.save()
        teacher.subject.set(subject_data)
        return teacher

    def update(self, instance, validated_data):
        subject_data = validated_data.pop('subject', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        print(validated_data)
        if subject_data is not None:
            instance.subject.set(subject_data)
        instance.save()
        return instance