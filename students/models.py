from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Department(models.Model):
    """Department model - e.g., Computer Science, Mathematics"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    established_date = models.DateField()
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(AbstractUser):
    """Extended User model for students"""
    # Personal Information
    student_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Academic Information
    enrollment_date = models.DateField(auto_now_add=True)
    graduation_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='students'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Remove username field and use email as the unique identifier
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'student_id', 'first_name', 'last_name']
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.student_id} - {self.get_full_name()}"

class Course(models.Model):
    """Course model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    credits = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE,
        related_name='courses'
    )
    instructor = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)  # e.g., "Fall 2024"
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    """Enrollment model - links students to courses with grades"""
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
        ('I', 'Incomplete'),
        ('W', 'Withdrawn'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrollment_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    
    class Meta:
        # Ensure a student can't enroll in the same course twice
        unique_together = ['student', 'course']
        ordering = ['course', 'student']
    
    def __str__(self):
        return f"{self.student} - {self.course}"