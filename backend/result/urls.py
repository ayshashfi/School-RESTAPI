from django.urls import path
from .views import (
    SyllabusListCreateView, SyllabusDetailView,
    ExamTypeListCreateView, ExamTypeDetailView,
    ExamListCreateView, ExamDetailView,
    ResultListCreateView, ResultDetailView,
    ResultListByStudentView, ResultListByExamView
)

urlpatterns = [
    path('syllabus/', SyllabusListCreateView.as_view(), name='syllabus-list-create'),
    path('syllabus/<int:pk>/', SyllabusDetailView.as_view(), name='syllabus-detail'),
    path('exam-type/', ExamTypeListCreateView.as_view(), name='exam-type-list-create'),
    path('exam-type/<int:pk>/', ExamTypeDetailView.as_view(), name='exam-type-detail'),
    path('exam/', ExamListCreateView.as_view(), name='exam-list-create'),
    path('exam/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('result/', ResultListCreateView.as_view(), name='result-list-create'),
    path('result/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
    path('results/student/<int:student_id>/', ResultListByStudentView.as_view(), name='result-list-by-student'),
    path('results/exam/<int:exam_id>/', ResultListByExamView.as_view(), name='result-list-by-exam'),
]
