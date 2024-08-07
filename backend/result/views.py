from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Syllabus, ExamType, Exam, Result
from .serializers import SyllabusSerializer, ExamTypeSerializer, ExamSerializer, ResultSerializer

# Syllabus Views
class SyllabusListCreateView(generics.ListCreateAPIView):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated]

class SyllabusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated]

# ExamType Views
class ExamTypeListCreateView(generics.ListCreateAPIView):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]

class ExamTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]

# Exam Views
class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

# Result Views
class ResultListCreateView(generics.ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Result.objects.none()

        # Optional: Add custom filtering logic if needed
        return Result.objects.all()

class ResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

class ResultListByStudentView(generics.ListAPIView):
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Result.objects.none()

        student_id = self.kwargs.get('student_id')
        if not student_id:
            return Result.objects.none()

        # Ensure filtering is correct
        return Result.objects.filter(student_id=student_id)

class ResultListByExamView(generics.ListAPIView):
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Result.objects.none()

        exam_id = self.kwargs.get('exam_id')
        if not exam_id:
            return Result.objects.none()

        # Ensure filtering is correct
        return Result.objects.filter(exam_id=exam_id)
