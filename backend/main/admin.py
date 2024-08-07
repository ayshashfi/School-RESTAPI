from django.contrib import admin
from main.models import User, Student, Teacher, ClassRoom, Subject, TeacherFile
from .models import User

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(TeacherFile)
admin.site.register(ClassRoom)
admin.site.register(Subject)