from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from .models import Student, Course, Department, Enrollment
from .forms import StudentForm, CourseForm, EnrollmentForm

@login_required
def dashboard(request):
    """Main dashboard showing statistics"""
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_departments = Department.objects.count()
    
    # Students per department
    dept_stats = Department.objects.annotate(
        student_count=Count('students')
    ).values('name', 'student_count')
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course'
    ).order_by('-enrollment_date')[:10]
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_departments': total_departments,
        'dept_stats': dept_stats,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'students/dashboard.html', context)

# Student Views
@login_required
def student_list(request):
    """List all students with search and filter"""
    students = Student.objects.select_related('department').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by department
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        students = students.filter(department_id=dept_filter)
    
    departments = Department.objects.all()
    
    context = {
        'students': students,
        'departments': departments,
        'search_query': search_query,
        'dept_filter': dept_filter,
    }
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, pk):
    """View student details with their enrollments"""
    student = get_object_or_404(
        Student.objects.prefetch_related('enrollments__course'),
        pk=pk
    )
    enrollments = student.enrollments.select_related('course').all()
    
    # Calculate GPA
    grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
    total_points = 0
    total_credits = 0
    
    for enrollment in enrollments:
        if enrollment.grade in grade_points:
            total_points += grade_points[enrollment.grade] * enrollment.course.credits
            total_credits += enrollment.course.credits
    
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'gpa': gpa,
    }
    return render(request, 'students/student_detail.html', context)

@staff_member_required
def student_add(request):
    """Add new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.get_full_name()} added successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})

@staff_member_required
def student_edit(request, pk):
    """Edit student"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/student_form.html', {
        'form': form, 
        'title': 'Edit Student',
        'student': student
    })

@staff_member_required
def student_delete(request, pk):
    """Delete student"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    
    return render(request, 'students/student_confirm_delete.html', {'student': student})

# Course Views
@login_required
def course_list(request):
    """List all courses"""
    courses = Course.objects.select_related('department').annotate(
        student_count=Count('enrollments')
    ).all()
    
    # Filter by department
    dept_filter = request.GET.get('department', '')
    if dept_filter:
        courses = courses.filter(department_id=dept_filter)
    
    departments = Department.objects.all()
    
    context = {
        'courses': courses,
        'departments': departments,
    }
    return render(request, 'students/course_list.html', context)

@login_required
def course_detail(request, pk):
    """View course details with enrolled students"""
    course = get_object_or_404(Course, pk=pk)
    enrollments = course.enrollments.select_related('student').all()
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'students/course_detail.html', context)

@staff_member_required
def course_add(request):
    """Add new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.code} added successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    
    return render(request, 'students/course_form.html', {'form': form, 'title': 'Add Course'})

# Enrollment Views
@staff_member_required
def enroll_student(request):
    """Enroll a student in a course"""
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(
                request, 
                f'Student enrolled in {enrollment.course.code} successfully!'
            )
            return redirect('student_detail', pk=enrollment.student.pk)
    else:
        form = EnrollmentForm()
    
    return render(request, 'students/enrollment_form.html', {'form': form})

@staff_member_required
def update_grade(request, pk):
    """Update student's grade"""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        grade = request.POST.get('grade')
        if grade:
            enrollment.grade = grade
            enrollment.save()
            messages.success(request, 'Grade updated successfully!')
    return redirect('student_detail', pk=enrollment.student.pk)