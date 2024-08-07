from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username, 
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Subject(models.Model):
    subject = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class User(AbstractUser):
    username = models.CharField(_('username'), max_length=30)
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(_('password'), max_length=255, blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    # objects = MyAccountManager()

    def __str__(self):
        return self.email
    

class Teacher(User):
    subject = models.ManyToManyField(Subject, blank=True)
    joined_date = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/teacher', null=True, blank=True)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return self.username


class TeacherFile(models.Model):
    teacher = models.ForeignKey(Teacher, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='teacher_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ClassRoom(models.Model):
    class_no = models.IntegerField()
    section = models.CharField(max_length=1, null=True, blank=True)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['class_no']
    
    def __str__(self):
        return f'{self.class_no} {self.section}'
    
    def get_class(self):
        return f'{self.class_no} {self.section}'
    
    def clean(self):
        if ClassRoom.objects.filter(class_no=self.class_no, section=self.section).exclude(id=self.id).exists():
            raise ValidationError(f"ClassRoom with class_no {self.class_no} and section {self.section} already exists.")

    def is_full(self):
        MAX_STUDENTS_PER_CLASS = 30
        return self.student_set.count() >= MAX_STUDENTS_PER_CLASS
    
    def class_strength(self):
        return self.student_set.count()
    
    def syllabus_count(self):
        return self.syllabus_set.count()

class Student(User):
    roll_no = models.IntegerField(unique=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.DO_NOTHING)
    admission_date = models.DateField()
    parent_contact = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/student', null=True, blank=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        
        ordering = ['roll_no']
    
    def __str__(self):
        return self.username
    