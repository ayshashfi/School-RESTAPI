from django.contrib import admin
from .models import Syllabus, Exam, Result, ExamType

class ExamAdmin(admin.ModelAdmin):
    list_display = ('class_room', 'subject', 'exam_type')
    list_filter = ('exam_type', 'class_room', 'subject')

class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('class_room', 'subject', 'description')
    list_filter = ('class_room', 'subject')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'pass_or_fail')
    list_filter = ('exam', 'pass_or_fail')
    search_fields = ('student__username', 'exam__subject__subject')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'exam')

    def student(self, obj):
        return obj.student.username

    student.short_description = 'Student'

admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(ExamType)
