from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.shortcuts import get_object_or_404
from django.http.response import JsonResponse

from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, EmailMessage

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Student, Teacher, ClassRoom, Subject, TeacherFile
from .serializers import PasswordResetSerializer, UserSerializer, StudentSerializer, TeacherSerializer, ClassroomSerializer, SubjectSerializer, TeacherFileSerializer
from .tasks import send_password_set_email

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['id'] = user.id
        token['is_admin'] = user.is_admin
        token['is_student'] = user.is_student
        token['is_teacher'] = user.is_teacher

        return token
        
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
   
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

def send_password_set_email(user):
    email = user.email
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    current_site = 'http://127.0.0.1:8000/'
    mail_subject = "Reset your password"

    link = f'http://localhost:3000/create-new-password/?uid={uid}&token={token}'
    print(link, 'link---------')

    context = {
        "link": link,
        "username": user.username
    }
    subject = "Password reset email"
    html_body = render_to_string("email/set_password.html", context)
    email_message = EmailMessage(
                subject=subject,
                body=html_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
    
    email_message.content_subtype = 'html'
    email_message.send(fail_silently=False)
        
    return Response({"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK)

class StudentRegisterView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def perform_create(self, serializer):
        class_room = serializer.validated_data['class_room']
        
        # Check if the class is full
        if class_room.is_full():
            raise ValidationError(f"Class {class_room.get_class()} is full. Please assign the student to a different class or create a new section.")
        
        student = serializer.save(is_student=True)
        print(student, 'student')
        print(student.email, 'email')
        send_password_set_email(student)

class TeacherRegisterView(generics.CreateAPIView):
    # permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def perform_create(self, serializer):
        teacher = serializer.save(is_teacher=True)
        send_password_set_email(teacher)

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

class StudentListByClassView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_no, section):
        try:
            class_room = ClassRoom.objects.get(class_no=class_no, section=section)
        except ClassRoom.DoesNotExist:
            raise NotFound(detail="ClassRoom not found")
        
        students = Student.objects.filter(class_room=class_room)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

class StudentListUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Student, id=pk)


class StudentList(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class SubjectUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class TeacherList(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

class TeacherView(generics.RetrieveUpdateAPIView):
    serializer_class = TeacherSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Teacher, id=pk)
    

class TeacherFilesView(generics.ListAPIView):
    serializer_class = TeacherFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            return TeacherFile.objects.filter(teacher=user)
        return TeacherFile.objects.none()
    



class TeacherFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher_id')
        teacher = Teacher.objects.get(id=teacher_id)
        files = request.FILES.getlist('files')
        file_objects = []
        for file in files:
            file_obj = TeacherFile(teacher=teacher, file=file)
            file_obj.save()
            file_objects.append(file_obj)
        serializer = TeacherFileSerializer(file_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TeacherDetailView(APIView):
    def get(self, request, teacher_id, *args, **kwargs):
        teacher = Teacher.objects.get(id=teacher_id)
        serializer = TeacherSerializer(teacher)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BlockUserView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = False
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UnBlockUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class ClassRoomAPIView(generics.ListCreateAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassroomSerializer
   


class ClassUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClassRoom.objects.all()
    serializer_class = ClassroomSerializer
    
   