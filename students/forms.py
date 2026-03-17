from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Student, Course, Department, Enrollment

class StudentForm(UserCreationForm):
    """Form for creating/editing students"""
    
    class Meta(UserCreationForm.Meta):
        model = Student
        fields = ('email', 'username', 'first_name', 'last_name', 'student_id',
                 'phone_number', 'address', 'date_of_birth', 'department')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help texts
        for field in self.fields.values():
            field.help_text = ''

class StudentChangeForm(UserChangeForm):
    """Form for editing existing students"""
    
    class Meta(UserChangeForm.Meta):
        model = Student
        fields = ('email', 'first_name', 'last_name', 'phone_number',
                 'address', 'date_of_birth', 'department', 'is_active')

class CourseForm(forms.ModelForm):
    """Form for creating/editing courses"""
    
    class Meta:
        model = Course
        fields = ('code', 'name', 'description', 'credits', 
                 'department', 'instructor', 'semester')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EnrollmentForm(forms.ModelForm):
    """Form for enrolling students in courses"""
    
    class Meta:
        model = Enrollment
        fields = ('student', 'course')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show active students only
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        # Show courses that don't have prerequisites to simplify
        self.fields['course'].queryset = Course.objects.all()
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        
        # Check if student is already enrolled
        if student and course:
            if Enrollment.objects.filter(student=student, course=course).exists():
                raise forms.ValidationError(
                    f"{student} is already enrolled in {course}"
                )
        return cleaned_data