from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Attendance
from main.models import Student, ClassRoom
from .serializers import AttendanceSerializer
from main.serializers import StudentSerializer
from datetime import date
import datetime


class StudentListByClassAndDate(APIView):
    def get(self, request, class_id, date_str):
        class_room = ClassRoom.objects.get(id=class_id)
        students = Student.objects.filter(class_room=class_room)
        attendance_date = date.fromisoformat(date_str)
        attendance_records = Attendance.objects.filter(student__in=students, date=attendance_date)
        student_serializer = StudentSerializer(students, many=True)
        attendance_serializer = AttendanceSerializer(attendance_records, many=True)
        return Response({
            'students': student_serializer.data,
            'attendance': attendance_serializer.data
        })

class TakeAttendance(APIView):

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ViewAttendance(APIView):
    def get(self, request, class_id, date):
        attendance_records = Attendance.objects.filter(student__class_room_id=class_id, date=date)
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, class_id, date):
        today = datetime.date.today()
        print(today)
        for record in request.data:
            attendance = Attendance.objects.get(student_id=record['student'], date=date)
            attendance.present = record['present']
            attendance.save()
        return Response(status=status.HTTP_200_OK)


class StudentAttendanceView(APIView):
    def get(self, request, student_id, date=None):
        if date:
            attendance_records = Attendance.objects.filter(student_id=student_id, date=date)
        else:
            attendance_records = Attendance.objects.filter(student_id=student_id)
        
        serializer = AttendanceSerializer(attendance_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)