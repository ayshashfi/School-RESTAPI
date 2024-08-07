from django.db import models
from main.models import ClassRoom, Teacher, Student, Subject

class Syllabus(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Syllabus for {self.class_room} - {self.subject}"

class ExamType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    date = models.DateField()
    maximum_marks = models.IntegerField()

    class Meta:
        unique_together = ('class_room', 'subject', 'exam_type', 'date')

    def __str__(self):
        return f"{self.exam_type} - {self.class_room} - {self.subject} on {self.date}"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True)
    marks_obtained = models.IntegerField()
    pass_or_fail = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"Result for {self.student} in {self.exam}"

    def save(self, *args, **kwargs):
        if self.exam:
            if self.marks_obtained < 0:
                raise ValueError("Marks obtained cannot be negative.")
            if self.marks_obtained > self.exam.maximum_marks:
                raise ValueError("Marks obtained cannot exceed maximum marks.")
            self.pass_or_fail = self.marks_obtained >= self.exam.maximum_marks * 0.4
        super().save(*args, **kwargs)
